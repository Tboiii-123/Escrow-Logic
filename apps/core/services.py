from django.db import transaction

from .models import Escrow, EscrowEvent
from django.core.exceptions import ValidationError
from rest_framework.response import Response


class EscrowService:

    @staticmethod
    @transaction.atomic
    def create_escrow(
        tenant_id,
        landlord_id,
        property_id,
        amount,
        currency="NGN"
    ):
        """
        Create a new escrow transaction and log the event.
        """

        escrow = Escrow.objects.create(
            tenant_id=tenant_id,
            landlord_id=landlord_id,
            property_id=property_id,
            amount=amount,
            currency=currency,
            status=Escrow.Status.CREATED,
        )

        EscrowEvent.objects.create(
            escrow=escrow,
            event_type=EscrowEvent.EventType.CREATED,
            metadata={
                "action": "Escrow created successfully"
            }

            
        )

        return escrow



        
    @staticmethod
    @transaction.atomic
    def fund_escrow(escrow_id, tenant_id, idempotency_key=None):
        """
        Fund escrow after payment confirmation.
        This is idempotent: repeated calls won't double-process.
        """

        escrow = Escrow.objects.select_for_update().get(id=escrow_id)

        if  tenant_id != escrow.tenant_id:
                raise ValidationError(
                 "Only the escrow tenant can fund this escrow"
                    
                )
                

        # 1. Check if already processed (IDEMPOTENCY CHECK)
        if idempotency_key:
            existing = EscrowEvent.objects.filter(
                escrow=escrow,
                event_type=EscrowEvent.EventType.FUNDED,
                idempotency_key=idempotency_key
            ).first()

            if existing:
                raise ValidationError(
                    
                            "Already processed idempotent request"
                )

        # 2. Validate state
        if escrow.status != Escrow.Status.CREATED:
            raise ValidationError(
                f"Cannot fund escrow in state {escrow.status}"
            )

        # 3. Update state
        escrow.status = Escrow.Status.HELD
        escrow.save(update_fields=["status"])

        # 4. Log event with idempotency key
        EscrowEvent.objects.create(
            escrow=escrow,
            event_type=EscrowEvent.EventType.FUNDED,
            idempotency_key=idempotency_key,
            metadata={
                "action": "Payment confirmed and funds held"
            }


        )

        return escrow




    @staticmethod
    @transaction.atomic
    def confirm_trigger(escrow_id, triggered_by=None, idempotency_key=None):
        """
        Confirm that the escrow condition has been met.
        Example: property inspection completed.
        """

        escrow = Escrow.objects.select_for_update().get(id=escrow_id)

        if escrow.status != Escrow.Status.HELD:
            raise ValidationError(
                f"Cannot trigger escrow in '{escrow.status}' state."
            )

        escrow.status = Escrow.Status.TRIGGERED
        escrow.save(update_fields=["status"])

        EscrowEvent.objects.create(
            escrow=escrow,
            event_type=EscrowEvent.EventType.TRIGGERED,
               idempotency_key=idempotency_key,
          metadata = {
                "action": "trigger_confirmed",
                "actor_id": str(triggered_by),

}

        )

        return escrow


    @staticmethod
    @transaction.atomic
    def release_funds(escrow_id,landlord_id, idempotency_key=None):

        escrow = Escrow.objects.select_for_update().get(id=escrow_id)


        if landlord_id != escrow.landlord_id:
                raise ValidationError(
                "Only the escrow landlord can release funds"
                    
                )

        # 1. IDEMPOTENCY CHECK
        if idempotency_key:
            existing = EscrowEvent.objects.filter(
                escrow=escrow,
                event_type=EscrowEvent.EventType.RELEASED,
                idempotency_key=idempotency_key
            ).first()

            if existing:
                   raise ValidationError(
                    
                            "Already released"
                )

        # 2. STATE VALIDATION
        if escrow.status != Escrow.Status.TRIGGERED:
            raise ValidationError(
                f"Cannot release escrow in state {escrow.status}"
            )

        # 3. UPDATE STATE
        escrow.status = Escrow.Status.RELEASED
        escrow.save(update_fields=["status"])

        # 4. LOG EVENT
        EscrowEvent.objects.create(
            escrow=escrow,
            event_type=EscrowEvent.EventType.RELEASED,
            idempotency_key=idempotency_key,
            # metadata={
            #     "message": "Funds released to landlord"
            # }

        )

        return escrow


    @staticmethod
    @transaction.atomic
    def refund_funds(escrow_id,  tenant_id, idempotency_key=None):

        escrow = Escrow.objects.select_for_update().get(id=escrow_id)

        if tenant_id != escrow.tenant_id:
            raise ValidationError(
             "Only the escrow tenant can request refund"

                
            )
            

        # 1. IDEMPOTENCY CHECK
        if idempotency_key:
            existing = EscrowEvent.objects.filter(
                escrow=escrow,
                event_type=EscrowEvent.EventType.REFUNDED,
                idempotency_key=idempotency_key
            ).first()

            if existing:
                  raise ValidationError(
                "Already refunded"
            )

        # 2. STATE VALIDATION
        if escrow.status == Escrow.Status.RELEASED:
            raise ValidationError("Cannot refund after release")

        if escrow.status not in [
            Escrow.Status.HELD,
            Escrow.Status.TRIGGERED,
             Escrow.Status.DISPUTED
        ]:
            raise ValidationError(
                f"Cannot refund escrow in state {escrow.status}"
            )

        # 3. UPDATE STATE
        escrow.status = Escrow.Status.REFUNDED
        escrow.save(update_fields=["status"])

        # 4. LOG EVENT
        EscrowEvent.objects.create(
            escrow=escrow,
            event_type=EscrowEvent.EventType.REFUNDED,
            idempotency_key=idempotency_key,
            # metadata={
            #     "message": "Funds refunded to tenant"
            # }

        )

        return escrow


    @staticmethod
    @transaction.atomic
    def dispute_escrow(escrow_id, idempotency_key=None):

        escrow = Escrow.objects.select_for_update().get(id=escrow_id)

        # 1. IDEMPOTENCY CHECK
        if idempotency_key:
            existing = EscrowEvent.objects.filter(
                escrow=escrow,
                event_type="disputed",
                idempotency_key=idempotency_key
            ).first()

            if existing:
                return escrow  # already processed safely

        # 2. STATE VALIDATION
        if escrow.status in ["released", "refunded"]:
            raise ValidationError("Cannot dispute completed escrow")

        if escrow.status == "created":
            raise ValidationError("Cannot dispute before funding")

        # 3. UPDATE STATE
        escrow.status = "disputed"
        escrow.save(update_fields=["status"])

        # 4. LOG EVENT
        EscrowEvent.objects.create(
            escrow=escrow,
            event_type="disputed",
            idempotency_key=idempotency_key,
            metadata={
                "message": "Escrow marked as disputed"
            }
        )

        return escrow








   