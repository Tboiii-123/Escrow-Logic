from django.urls import path

from .views import (
    create_escrow,
    fund_escrow,
    confirm_trigger,
    release_escrow,
    refund_escrow,

    escrow_status,


)

urlpatterns = [
    path("create/", create_escrow, name='create_escrow'),

    path("<uuid:escrow_id>/fund/",fund_escrow,name='fund_escrow'),

    path("<uuid:escrow_id>/trigger/",confirm_trigger,name='confirm_trigger'),

    path("<uuid:escrow_id>/release/",release_escrow,name='release_escrow'),

    path("<uuid:escrow_id>/refund/",refund_escrow,name='refund_escrow'),

    path("<uuid:escrow_id>/status/",escrow_status,name='escrow_status'),


]