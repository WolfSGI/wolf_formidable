from wolf_form import trigger


def test_triggers_natural_order():

    class MyForm:

        @trigger(name='whatever', title='This is really a whatever')
        def whatever(self):
            pass

        @trigger(name='something', title='This is really somthing !')
        def something(self):
            pass


    form = MyForm()
    assert trigger.find(form) == [
        (
            {
                'name': 'something',
                'order': 0,
                'title': 'This is really somthing !',
            },
            form.something
        ),
        (
            {
                'name': 'whatever',
                'order': 0,
                'title': 'This is really a whatever',
            },
            form.whatever
        ),
    ]


def test_triggers_forced_order():

    class MyForm:

        @trigger(
            name='whatever', title='This is really a whatever', order=1)
        def whatever(self):
            pass

        @trigger(
            name='something', title='This is really somthing !', order=2)
        def something(self):
            pass

        @trigger(
            name='alpha', title='And omega ?', order=3)
        def alpha(self):
            pass


    form = MyForm()
    assert trigger.find(form) == [
        (
            {
                'name': 'whatever',
                'order': 1,
                'title': 'This is really a whatever',
            },
            form.whatever
        ),
        (

            {
                'name': 'something',
                'order': 2,
                'title': 'This is really somthing !',
            },
            form.something
        ),
        (
            {
                'name': 'alpha',
                'order': 3,
                'title': 'And omega ?',
            },
            form.alpha
        ),
    ]
