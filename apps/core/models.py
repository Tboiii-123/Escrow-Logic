import uuid
from django.db import models
import uuid
from django.db import models
from apps.accounts.models import User


class Escrow(models.Model):

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        HELD = "held", "Held"
        TRIGGERED = "triggered", "Triggered"
        RELEASED = "released", "Released"
        REFUNDED = "refunded", "Refunded"
        DISPUTED = "disputed", "Disputed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant_id= models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="escrows_as_tenant",
    
    )

    landlord_id= models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="escrows_as_landlord",
    
    )

    property_id = models.UUIDField(db_index=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["landlord_id", "status"]),
        ]

    def __str__(self):
        return f"Escrow({self.id}) - {self.status}"


class EscrowEvent(models.Model):

    class EventType(models.TextChoices):
        CREATED = "created", "Created"
        FUNDED = "funded", "Funded"
        TRIGGERED = "triggered", "Triggered"
        RELEASED = "released", "Released"
        REFUNDED = "refunded", "Refunded"
        DISPUTED = "disputed", "Disputed"

    

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    escrow = models.ForeignKey(
        "Escrow",
        on_delete=models.CASCADE,
        related_name="events",
        db_index=True
    )

    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        db_index=True
    )

    idempotency_key = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["escrow", "created_at"]),
        ]

    def __str__(self):
        return f"{self.id} - {self.event_type}"