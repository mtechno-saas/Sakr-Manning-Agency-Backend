from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    RegisterView,
    LogoutView,
    GoogleAuthView,
    ContractViewSet,
    ReferenceViewSet,
    SeaServiceViewSet,
    CertificateViewSet,
    RankViewSet,
    InterviewViewSet,
    FinanceRecordViewSet,
    CVSubmissionViewSet,
    DeclarationViewSet,
    GlobalSearchView,
    get_all_users,
    create_user,
    get_filter_users,
    user_detail,
    assign_rank,
    get_user_certificates,
    get_user_ranks,
    add_user_certificate,
    add_user_rank,
    remove_user_certificate,
    remove_user_rank,
    assign_rank_by_position,
    DocumentViewSet, 
    LanguageProficiencyViewSet,
    UserLanguageViewSet,
    PersonalDocumentViewSet,
    VerifyEmailView,
    get_positions,
    get_flags,
    get_vessel_types,
    get_company_types,
    get_coc_choices,
    get_document_types,
    NextOfKinViewSet
)
from .application_views import SeafarerApplicationViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="user")
router.register(r'contracts', ContractViewSet, basename="contract")
router.register(r'references', ReferenceViewSet, basename="reference")
router.register(r'sea-services', SeaServiceViewSet, basename="seaservice")
router.register(r'certificates', CertificateViewSet, basename="certificate")
router.register(r'ranks', RankViewSet, basename="rank")
# NOTE: companies route is handled by the companies app (includes stats endpoint)
router.register(r'interviews', InterviewViewSet, basename="interview")
router.register(r'finance-records', FinanceRecordViewSet, basename="financerecord")
router.register(r'cv-submissions', CVSubmissionViewSet, basename="cvsubmission")
router.register(r'declarations', DeclarationViewSet, basename="declaration")
router.register(r'documents', DocumentViewSet, basename="document")
router.register(r'my-languages', LanguageProficiencyViewSet, basename='my-languages')
router.register(r'user-languages', UserLanguageViewSet, basename="userlanguage")
router.register(r'personal-documents', PersonalDocumentViewSet, basename="personaldocument")
router.register(r'next-of-kin', NextOfKinViewSet, basename="nextofkin")
router.register(r'seafarer-application', SeafarerApplicationViewSet, basename="seafarer-application")
urlpatterns = [
    path('', include(router.urls)),
    path('global-search/', GlobalSearchView.as_view(), name='global-search'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),
    path('all/', get_all_users, name='get_all_users'),
    path('create/', create_user, name='create_user'),
    path('filter/', get_filter_users, name='get_filter_users'),
    path('users/<int:pk>/', user_detail, name='user-detail'),
    path('users/<int:user_id>/assign-rank/<int:rank_id>/', assign_rank, name='assign-rank'),
    # Compatibility routes for frontend (matching /api/users/declarations/ and /api/users/certificates/)
    path('users/declarations/', DeclarationViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-declarations-list'),
    path('users/declarations/<int:pk>/', DeclarationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='user-declarations-detail'),
    path('users/certificates/', CertificateViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-certificates-list'),
    path('users/certificates/<int:pk>/', CertificateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='user-certificates-detail'),

    # User-specific certificate and rank endpoints
    path('users/<int:user_id>/certificates/', get_user_certificates, name='user-certificates'),
    path('users/<int:user_id>/ranks/', get_user_ranks, name='user-ranks'),
    path('users/<int:user_id>/certificates/add/', add_user_certificate, name='add-user-certificate'),
    path('users/<int:user_id>/ranks/add/', add_user_rank, name='add-user-rank'),
    path('users/<int:user_id>/certificates/<int:certificate_id>/remove/', remove_user_certificate, name='remove-user-certificate'),
    path('users/<int:user_id>/ranks/<int:rank_id>/remove/', remove_user_rank, name='remove-user-rank'),
    path('users/<int:user_id>/assign-by-position/', assign_rank_by_position, name='assign-rank-by-position'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('positions/', get_positions, name='get-positions'),
    path('flags/', get_flags, name='get-flags'),
    path('company-types/', get_company_types, name='get-company-types'),
    path('vessel-types/', get_vessel_types, name='get-vessel-types'),
    path('coc-choices/', get_coc_choices, name='get-coc-choices'),
    path('document-types/', get_document_types, name='get-document-types'),
]
