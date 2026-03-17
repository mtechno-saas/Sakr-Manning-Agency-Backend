from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from api.models import Users
from .schemas import ContractData
from .utils import fill_contract
import os
import uuid
import glob
from datetime import datetime

class GenerateContractView(APIView):
    def post(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        
        # 1. Map User to ContractData
        try:
            contract_data = ContractData(
                full_name=f"{user.first_name} {user.middle_name}".strip(),
                date_of_birth=user.date_of_birth or "2000-01-01", # Fallback or handle error
                marital_status=user.marital_status,
                nationality=user.nationality or "N/A",
                height_cm=float(user.Height_Cm or 0),
                weight_kg=float(user.Weight_Kg or 0),
                place_of_birth=user.Place_Of_Birth or "N/A",
                shirt_size=user.shirt_size or "N/A",
                trouser_size=user.trouser_size or "N/A",
                shoe_size=user.shoes_size or "N/A",
                
                education=user.college_or_school,
                english_fluency=user.english_language_level or "Good",
                
                address=user.address or "N/A",
                email=user.email,
                phone_number=user.phone_number,
                
                passport_number=user.passport_no,
                passport_issue_date=user.passport_issue_date,
                passport_expiry_date=user.passport_expiry_date,
                passport_issued_by=user.passport_issued_by,
                
                seaman_book_number=user.seaman_book_no,
                seaman_book_issue_date=user.seaman_book_issue_date,
                seaman_book_expiry_date=user.seaman_book_expiry_date,
                seaman_book_issued_by=user.seaman_book_issued_by,
                
                next_of_kin_name=user.next_of_kin_full_name or "N/A",
                next_of_kin_relationship=user.next_of_kin_relationship or "N/A",
                next_of_kin_address=user.next_of_kin_address_country or "N/A",
                next_of_kin_phone=user.next_of_kin_phone or "N/A"
            )
        except Exception as e:
            return Response({"error": f"Data validation error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Define Paths
        template_path = os.path.join(settings.BASE_DIR, "contracts", "contract", "A NEW APPLICATION - Copy (5).docx")
        output_dir = os.path.join(settings.MEDIA_ROOT, "contracts", "generated")
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"Contract_{user.id}_{uuid.uuid4().hex[:8]}.docx"
        output_path = os.path.join(output_dir, filename)
        
        # 3. Generate Doc
        try:
            fill_contract(template_path, output_path, contract_data)
        except Exception as e:
            return Response({"error": f"Generation error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        # 4. Return File URL
        file_url = f"{settings.MEDIA_URL}contracts/generated/{filename}"
        
        return Response({
            "message": "Contract generated successfully",
            "file_url": file_url,
            "file_path": output_path
        }, status=status.HTTP_200_OK)

class ListGeneratedContractsView(APIView):
    def get(self, request):
        output_dir = os.path.join(settings.MEDIA_ROOT, "contracts", "generated")
        if not os.path.exists(output_dir):
            return Response([], status=status.HTTP_200_OK)
            
        files = glob.glob(os.path.join(output_dir, "*.docx"))
        contracts = []
        for f in files:
            filename = os.path.basename(f)
            created_at = datetime.fromtimestamp(os.path.getctime(f)).strftime('%Y-%m-%d %H:%M:%S')
            file_url = f"{settings.MEDIA_URL}contracts/generated/{filename}"
            
            contracts.append({
                "filename": filename,
                "created_at": created_at,
                "url": file_url
            })
            
        # Sort by creation time desc
        contracts.sort(key=lambda x: x['created_at'], reverse=True)
        
        return Response(contracts, status=status.HTTP_200_OK)
