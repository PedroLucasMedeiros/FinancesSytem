from rest_framework.routers import Route, SimpleRouter


class SingletonRouter(SimpleRouter):
    """Router para recursos sem {id}: /recurso/ -> create/retrieve/update/destroy.

    O DRF só liga os métodos que a ViewSet realmente implementa, então cada
    view expõe apenas os verbos das mixins que herda.
    """

    routes = [
        Route(
            url=r"^{prefix}{trailing_slash}$",
            mapping={
                "get": "retrieve",
                "post": "create",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            },
            name="{basename}-detail",
            detail=True,
            initkwargs={"suffix": "Instance"},
        ),
    ]