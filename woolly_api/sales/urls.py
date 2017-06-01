from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import WoollyUserTypeViewSet, SaleViewSet, AssociationViewSet, ItemViewSet, ItemSpecificationsViewSet
from .views import AssociationRelationshipView, SaleRelationshipView, ItemSpecificationsRelationshipView
from .views import WoollyUserTypeRelationshipView, AssociationRelationshipView, ItemRelationshipView, api_root

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

urlpatterns = [
    # Root
    url(r'^$', api_root),
    # Associations
    url(r'^assos/$', association_list, name='association-list'),
    url(r'^sales/$', sale_list, name='sale-list'),
    url(r'^sales/(?P<pk>[0-9]+)$', sale_detail, name='sale-detail'),
    # Items
    url(r'^items/$', item_list, name='item-list'),
    url(r'^items/(?P<pk>[0-9]+)$', item_detail, name='item-detail'),
    url(r'^sales/(?P<sale_pk>[0-9]+)/items/$', item_list, name='item-list'),

    # Spec
    url(r'^items/(?P<item_pk>[0-9]+)/spec/$',
        itemSpecifications_list, name='itemSpecification-list'),
    url(r'^spec/(?P<itemspec_pk>[0-9]+)/utype/$',
        usertype_list, name='usertype-list'),
    url(r'^assos/(?P<pk>[0-9]+)/$',
        association_detail, name='association-detail'),
    url(r'^assos/(?P<association_pk>[0-9]+)/sales/$',
        sale_list, name='sale-list'),
    url(r'^assos/(?P<association_pk>[0-9]+)/sales/(?P<pk>[0-9]+)$',
        sale_detail, name='sale-detail'),
    url(r'^assos/(?P<association_pk>[0-9]+)/sales/(?P<sale_pk>[0-9]+)/items/$',
        item_list, name='item-list'),
    url(r'^assos/(?P<association_pk>[0-9]+)/sales/(?P<sale_pk>[0-9]+)/items/(?P<pk>[0-9]+)$',
        item_detail, name='item-detail'),
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
    )
]
