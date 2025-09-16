from django.db.models import Count, F
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import mixins, viewsets, filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from planitarium_service.models import AstronomyShow, ShowTheme, PlanetariumDome, ShowSession, Reservation
from planitarium_service.serializers import ShowThemeSerializer, \
    PlanetariumDomeSerializer, ShowSessionSerializer, ShowSessionRetrieveSerializer, \
    ReservationSerializer, ShowSessionListSerializer, AstronomyShowListSerializer, AstronomyShowSerializer, \
    ReservationRetrieveSerializer, ReservationListSerializer


def search_schema(description: str):
    return extend_schema_view(
        list=extend_schema(
            parameters=[
                OpenApiParameter(
                    name='search',
                    description=description,
                    required=False,
                    type=str
                )
            ]
        )
    )


@search_schema("Search by title")
class AstronomyShowView(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("themes",)
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        return AstronomyShowSerializer


@search_schema("Search by name")
class ShowThemeView(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

class PlanetariumDomeView(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


@search_schema("Search by astronomy show title")
class ShowSessionSerializerView(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["astronomy_show__title"]

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return queryset.select_related("planetarium_dome", "astronomy_show").annotate(
                tickets_available=F("planetarium_dome__rows") * F("planetarium_dome__seat_in_row")
                                  - Count("tickets", distinct=True)
            )
        return queryset.select_related("planetarium_dome", "astronomy_show").order_by("id")

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionRetrieveSerializer
        return ShowSessionSerializer


class ReservationView(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet
                      ):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        if self.action == "retrieve":
            return ReservationRetrieveSerializer

        return ReservationSerializer


    def get_queryset(self):
        return self.queryset.select_related("user").prefetch_related("tickets__show_session__planetarium_dome").filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


