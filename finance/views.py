from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FinanceRecord
from .serializers import FinanceRecordSerializer


class FinanceRecordViewSet(viewsets.ModelViewSet):
    queryset = FinanceRecord.objects.all()
    serializer_class = FinanceRecordSerializer

    # Custom endpoint: calculate without saving
    @action(detail=False, methods=["post"])
    def calculate(self, request):
        """
        Example payload:
        {
          "user": 1,
          "company": 2,
          "start_date": "2025-09-01",
          "end_date": "2025-09-10"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # build FinanceRecord object but don't save
        finance_record = FinanceRecord(
            user=serializer.validated_data["user"],
            company=serializer.validated_data["company"],
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
        )

        return Response({
            "total_days": finance_record.total_days,
            "daily_rate": finance_record.daily_rate,
            "total_money": finance_record.total_money
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='status')
    def status(self, request):
        """Get finance record counts by status"""
        if hasattr(request.user, 'role') and request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            records = FinanceRecord.objects.all()
        else:
            records = FinanceRecord.objects.filter(user=request.user)
            
        return Response({
            'pending': records.filter(status='Pending').count(),
            'paid': records.filter(status='Paid').count(),
            'overdue': records.filter(status='Overdue').count(),
            'cancelled': records.filter(status='Cancelled').count(),
            'total': records.count(),
        })
