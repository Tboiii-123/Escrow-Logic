from rest_framework import serializers
from .models import Escrow
from .services import EscrowService


class CreateEscrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escrow
        fields = ("landlord_id", "property_id", "amount")

    def create(self, validated_data):
        request = self.context["request"]

        return EscrowService.create_escrow(
            tenant_id=request.user,
            landlord_id=validated_data["landlord_id"],
            property_id=validated_data["property_id"],
            amount=validated_data["amount"],
        )

#For view
class EscrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escrow
        fields = "__all__"
        read_only_fields = (
            "id",
            "status",
            "created_at",
            "resolved_at",
        )


