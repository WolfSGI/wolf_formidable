"""Wolf Form
"""

from abc import ABC, abstractmethod
from typing import Mapping, Type
from fct_annotate import annotation
from kettu.datastructures import Data
from kettu.exceptions import HTTPError
from wolf.app.render.html import BoundResources
from wolf.abc.resolvers import APIView
from wolf.app.render import html, renderer
from wolf.abc.request import RequestProtocol
from wolf.abc.response import ResponseProtocol

from .formidable import FormRenderer, Button, BaseModel



@annotation('form_button')
class trigger:
    """Form Trigger, defining form actions to use as deform buttons.
    """
    name: str
    title: str
    order: int = 0

    @classmethod
    def find(cls, component):
        """Find decorated methods ordered by `order`.
        """
        return sorted(
            tuple(super().find(component)),
            key=lambda x: (x[0]["order"], x[0]["name"])
        )


class Form(ABC, APIView):
    """Form View using the trigger decorator to define form actions.
    """
    button_name = "__trigger__"

    def __init__(self):
        self.triggers = {}
        self.buttons = []

        for ann, func in trigger.find(self):
            self.triggers[(ann["name"], self.button_name)] = func
            self.buttons.append(
                Button(
                    type=self.button_name,
                    name=ann["name"],
                    title=ann["title"],
                    action=func,
                    validate=ann.get("validate", False),
                )
            )

    def get_initial_data(
            self,
            request: RequestProtocol,
            *, context=None
    ) -> Mapping:
        """Returns a mapping containing the initial form data.
        """
        return {}

    @abstractmethod
    def get_schema(
            self,
            request: RequestProtocol,
            *, context=None
    ) -> Type[BaseModel]:
        """Pydantic model on which the form is based.
        """

    def get_form(
            self,
            request: RequestProtocol,
            *, context=None
    ) -> FormRenderer:
        """Formidable FormRenderer object used to render the actual form.
        """
        return FormRenderer()

    @html
    @renderer
    def GET(
            self,
            request: RequestProtocol,
            *, context=None
    ) -> str:
        """Initial rendering of the form.
        """
        form = self.get_form(request, context=context)
        schema = self.get_schema(request, context=context)
        return form(schema, buttons=self.buttons)

    @html
    @renderer
    def POST(
            self,
            request: RequestProtocol,
            *, context=None
    ) -> str | ResponseProtocol:
        """Handling of the form submission through the POST method.
        """
        data = request.get(Data)
        for trigger_field, action in self.triggers.items():
            if trigger_field in data.form:
                try:
                    # A validating trigger receives the schema instance,
                    # any other trigger the raw (normalized) data tree.
                    if btn.validate:
                        payload = self.get_schema(request)(**data)
                    else:
                        payload = data
                    if arg:
                        return btn.action(request, payload, arg)
                    return btn.action(request, payload)
                except ValidationError as exc:
                    errors: dict[str, str] = {}
                    messages = self.get_messages(request)
                    for error in exc.errors():
                        # a cross-field validator can bind its error to a field
                        # by raising PydanticCustomError with {"field": "<path>"};
                        # otherwise a model-level error renders at the form top
                        ctx = error.get("ctx") or {}
                        loc = ctx.get("field") or ".".join(
                            str(part) for part in error["loc"])
                        errors.setdefault(loc, i18n.translate(error, messages))
                        html_form = self.get_form(request, values=data, errors=errors)
                        return html_form.render()

        raise HTTPError(400)
