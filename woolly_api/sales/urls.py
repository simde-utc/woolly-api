from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
    SaleViewSet, AssociationViewSet, ItemViewSet, ItemSpecificationsViewSet,
    AssociationRelationshipView, SaleRelationshipView,
    ItemSpecificationsRelationshipView, OrderRelationshipView,
    AssociationRelationshipView, ItemRelationshipView, api_root,
    OrderViewSet, OrderLineViewSet, OrderLineRelationshipView,
    OrderLineItemViewSet, PaymentMethodViewSet, PaymentMethodRelationshipView,
    AssociationMemberViewSet, AssociationMemberRelationshipView
)
from authentication.views import WoollyUserTypeViewSet

usertype_list = WoollyUserTypeViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
usertype_detail = WoollyUserTypeViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

sale_list = SaleViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
sale_detail = SaleViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

association_list = AssociationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
association_detail = AssociationViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

item_list = ItemViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
item_detail = ItemViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

itemSpecifications_list = ItemSpecificationsViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
itemSpecifications_detail = ItemSpecificationsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

order_list = OrderViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
order_detail = OrderViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

orderline_list = OrderLineViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
orderline_detail = OrderLineViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

orderlineitem_list = OrderLineItemViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
orderlineitem_detail = OrderLineItemViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

paymentmethod_list = PaymentMethodViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
paymentmethod_detail = PaymentMethodViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

associationmember_list = AssociationMemberViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
associationmember_detail = AssociationMemberViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    # Root
    url(r'^$', api_root),

    # Associations
    url(r'^assos/$', association_list, name='association-list'),
    url(r'^assos/(?P<pk>[0-9]+)/$',
        association_detail, name='association-detail'),
    url(r'^associationmembers/(?P<associationmember_pk>[0-9]+)/assos/$', association_list, name='association-list'),
    url(r'^associationmembers/(?P<associationmember_pk>[0-9]+)/assos/(?P<pk>[0-9]+)/$',
        association_detail, name='association-detail'),

    url(r'^associationmembers/$', associationmember_list, name='associationmember-list'),
    url(r'^associationmembers/(?P<pk>[0-9]+)/$',
        associationmember_detail, name='associationmember-detail'),

    # Sales
    url(r'^sales/$', sale_list, name='sale-list'),
    url(r'^sales/(?P<pk>[0-9]+)$', sale_detail, name='sale-detail'),
    url(r'^assos/(?P<association_pk>[0-9]+)/sales/$',
        sale_list, name='sale-list'),
    url(r'^assos/(?P<association_pk>[0-9]+)/sales/(?P<pk>[0-9]+)$',
        sale_detail, name='sale-detail'),
    url(r'^paymentmethods/(?P<payment_pk>[0-9]+)/sales/$',
        sale_list, name='sale-payment-list'),
    url(r'^paymentmethods/(?P<payment_pk>[0-9]+)/sales/(?P<pk>[0-9]+)$',
        sale_detail, name='sale-payment-detail'),

    # Items
    url(r'^items/$', item_list, name='item-list'),
    url(r'^items/(?P<pk>[0-9]+)$', item_detail, name='item-detail'),
    url(r'^sales/(?P<sale_pk>[0-9]+)/items/$', item_list, name='item-list'),
    url(r'^assos/(?P<association_pk>[0-9]+)/sales/(?P<sale_pk>[0-9]+)/items/$',
        item_list, name='item-list'),
    url(r'^assos/(?P<association_pk>[0-9]+)/sales/(?P<sale_pk>[0-9]+)/items/(?P<pk>[0-9]+)$',
        item_detail, name='item-detail'),

    # Spec
    url(r'^itemspecifications/$', itemSpecifications_list,
        name='itemSpecification-list'),
    url(r'^itemspecifications/(?P<pk>[0-9]+)$', itemSpecifications_detail,
        name='itemSpecification-detail'),
    url(r'^items/(?P<item_pk>[0-9]+)/itemspecifications/$',
        itemSpecifications_list, name='itemSpecification-list'),
    url(r'^itemspecifications/(?P<itemspec_pk>[0-9]+)/woollyusertypes/$',
        usertype_list, name='usertype-list'),

    # User Type
    url(r'^woollyusertypes/$',
        usertype_list, name='usertype-list'),
    url(r'^woollyusertypes/(?P<pk>[0-9]+)/$',
        usertype_detail, name='usertype-detail'),

    # Orders
    url(r'^users/(?P<woollyuser_pk>[0-9]+)/orders/$',
        order_list, name='order-list'),
    url(r'^users/(?P<woollyuser_pk>[0-9]+)/orders/(?P<pk>[0-9]+)$',
        order_detail, name='order-detail'),
    url(r'^orders/$',
        order_list, name='order-list'),
    url(r'^orders/(?P<pk>[0-9]+)/$',
        order_detail, name='order-detail'),

    # OrderLines
    url(r'^orderlines/$',
        orderline_list, name='orderline-list'),
    url(r'^orderlines/(?P<pk>[0-9]+)/$',
        orderline_detail, name='orderline-detail'),
    url(r'^orders/(?P<order_pk>[0-9]+)/lines/$',
        orderline_list, name='orderline-list'),
    url(r'^orders/(?P<order_pk>[0-9]+)/lines/(?P<pk>[0-9]+)$',
        orderline_detail, name='orderline-detail'),
    url(r'^orderlines/(?P<orderline_pk>[0-9]+)/items/$',
        orderlineitem_list, name='orderlineitem-list'),
    url(r'^orderlines/(?P<orderline_pk>[0-9]+)/lines/(?P<pk>[0-9]+)$',
        orderlineitem_detail, name='orderlineitem-detail'),

    # Payment Methods
    url(r'^paymentmethods/$',
        paymentmethod_list, name='paymentmethod-list'),
    url(r'^paymentmethods/(?P<pk>[0-9]+)/$',
        paymentmethod_detail, name='paymentmethod-detail'),
    url(r'^sales/(?P<sale_pk>[0-9]+)/paymentmethods/$',
        paymentmethod_list, name='paymentmethod-list'),
    url(r'^sales/(?P<sale_pk>[0-9]+)/paymentmethods/(?P<pk>[0-9]+)$',
        paymentmethod_detail, name='paymentmethod-detail'),

    # Relationships views for the related links
    url(
        regex=r'^assos/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        view=AssociationRelationshipView.as_view(),
        name='maison-relationships'
    ),
    url(
        regex=r'^assos/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        view=AssociationRelationshipView.as_view(),
        name='association-relationships'
    ),
    url(
        regex=r'^sales/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        view=SaleRelationshipView.as_view(),
        name='sale-relationships'
    ),
    url(
        regex=r'^items/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        view=ItemRelationshipView.as_view(),
        name='item-relationships'
    ),
    url(
        regex=r'^specs/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        view=ItemSpecificationsRelationshipView.as_view(),
        name='itemSpecification-relationships'
    ),
    url(
        regex=r'^orders/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        view=OrderRelationshipView.as_view(),
        name='order-relationships'
    ),
    url(
        regex=r'^orderlines/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        view=OrderLineRelationshipView.as_view(),
        name='orderline-relationships'
    ),
    url(
        regex=r'^paymentmethods/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        view=PaymentMethodRelationshipView.as_view(),
        name='paymentmethod-relationships'
    ),
    url(
        regex=r'^associationmembers/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        view=AssociationMemberRelationshipView.as_view(),
        name='associationmember-relationships'
    )
]
