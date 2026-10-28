from django.urls import path

from analytics.views import BacklogView, RequestsView, SlaView, ThroughputView

urlpatterns = [
    path("requests/", RequestsView.as_view(), name="analytics-requests"),
    path("throughput/", ThroughputView.as_view(), name="analytics-throughput"),
    path("backlog/", BacklogView.as_view(), name="analytics-backlog"),
    path("sla/", SlaView.as_view(), name="analytics-sla"),
]
