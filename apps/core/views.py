from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework import status

from .models import Escrow
from .serializers import EscrowSerializer,CreateEscrowSerializer
from .services import EscrowService

#Cretae Escrow
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_escrow(request):
    serializer = CreateEscrowSerializer(
        data=request.data,
        context={"request": request},
    )

    if serializer.is_valid():
        escrow = serializer.save()

        return Response(
            {
                "message": "Escrow created successfully",
                "data": EscrowSerializer(escrow).data,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


# POST /escrow/uuid:escrow_id/fund/

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def fund_escrow(request, escrow_id):
    try:
        
        escrow = EscrowService.fund_escrow(
            escrow_id=escrow_id,
            tenant_id=request.user,
            
            idempotency_key=request.headers.get("Idempotency-Key"),
            
        )

        return Response(EscrowSerializer(escrow).data)

    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

# POST /escrow/uuid:escrow_id/trigger/

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_trigger(request, escrow_id):
    try:
        escrow = EscrowService.confirm_trigger(
            escrow_id=escrow_id,
            triggered_by=request.user,
               idempotency_key=request.headers.get("Idempotency-Key"),
        )

        return Response(EscrowSerializer(escrow).data)

    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

# POST /escrow/uuid:escrow_id/release/

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def release_escrow(request, escrow_id):
    try:
        escrow = EscrowService.release_funds(
            escrow_id=escrow_id,
              landlord_id=request.user,
            idempotency_key=request.headers.get("Idempotency-Key"),
        )

        return Response(EscrowSerializer(escrow).data)

    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


        

#Refund
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refund_escrow(request, escrow_id):
    try:
        escrow = EscrowService.refund_funds(
            escrow_id=escrow_id,
              tenant_id=request.user,
            idempotency_key=request.headers.get("Idempotency-Key"),
        )

        return Response(EscrowSerializer(escrow).data)

    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

#Disputed
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def dispute_escrow(request, escrow_id):
    try:
        escrow = EscrowService.dispute_escrow(
            escrow_id=escrow_id,
            idempotency_key=request.headers.get("Idempotency-Key"),
        )

        return Response(EscrowSerializer(escrow).data)

    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def escrow_status(request, escrow_id):
    try:
        
        escrow = Escrow.objects.select_related("tenant_id", "landlord_id").get(id=escrow_id)

        # Only participants can view
        if request.user not in [
            escrow.tenant_id,
            escrow.landlord_id,
        ]:
            return Response(
                {"error": "You are not authorized to view this escrow"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EscrowSerializer(escrow)

        return Response(
            {
                "message": "Escrow retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Escrow.DoesNotExist:
        return Response(
            {"error": "Escrow not found"},
            status=status.HTTP_404_NOT_FOUND,
        )