from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404 # Not strictly needed here due to serializer validation
from .serializers import TipCreateSerializer, TipDetailSerializer
from .models import Tip
from decimal import Decimal

User = get_user_model()

class GiveTipView(generics.CreateAPIView):
    """
    API endpoint for users to give tips to other users.
    """
    serializer_class = TipCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # The serializer's context will have 'request' which is used in validate_tippee_id
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        tippee_id = validated_data['tippee_id']
        amount = validated_data['amount']
        message = validated_data.get('message', '') # Defaults to empty string if not provided

        tipper = request.user

        # Fetch tippee User instance. Serializer already validated existence and not self.
        tippee = User.objects.get(pk=tippee_id)

        try:
            with transaction.atomic():
                # Lock both tipper and tippee rows.
                # To avoid deadlocks, always lock rows in a consistent order (e.g., by primary key).
                user_ids_to_lock = sorted([tipper.id, tippee.id])

                # This queryset ensures that we only attempt to lock existing users.
                # It's important because select_for_update() on a non-existent row can behave differently across DBs.
                locked_users_qs = User.objects.filter(id__in=user_ids_to_lock).select_for_update().order_by('id')

                # Convert queryset to a dictionary for easy access after locking
                locked_users_map = {user.id: user for user in locked_users_qs}

                # Ensure both users were found and locked. This should always be true if IDs are valid.
                if tipper.id not in locked_users_map or tippee.id not in locked_users_map:
                    # This would be an unexpected state, possibly indicating one user was deleted mid-transaction
                    # by another process, despite FK constraints (if they are deferred or not strict).
                    # Or, more likely, an issue with the initial ID validation if it were not thorough.
                    return Response({"detail": "Could not lock user accounts for transaction."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                locked_tipper = locked_users_map[tipper.id]
                locked_tippee = locked_users_map[tippee.id]

                if locked_tipper.balance < amount:
                    # transaction.set_rollback(True) # Not strictly necessary with atomic block raising error
                    return Response({"detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

                # Perform balance updates
                locked_tipper.balance -= amount
                locked_tippee.balance += amount

                locked_tipper.save(update_fields=['balance'])
                locked_tippee.save(update_fields=['balance'])

                # Create the Tip record
                tip = Tip.objects.create(
                    tipper=locked_tipper,
                    tippee=locked_tippee,
                    amount=amount,
                    message=message
                )

            tip_detail_serializer = TipDetailSerializer(tip, context={'request': request})
            return Response(tip_detail_serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            # Log e for server-side debugging
            print(f"Database IntegrityError during tip transaction: {e}")
            return Response({"detail": "A database integrity error occurred. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"Unexpected error during tip transaction: {e}")
            return Response({"detail": "An unexpected error occurred. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SentTipsListView(generics.ListAPIView):
    """
    API endpoint for users to view tips they have sent.
    """
    serializer_class = TipDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Prefetch related tipper and tippee for efficiency, as TipDetailSerializer will access them.
        # Since tipper is always self.request.user, prefetching it might be less critical here,
        # but prefetching tippee is good.
        return Tip.objects.filter(tipper=self.request.user).select_related('tipper', 'tippee').order_by('-timestamp')


class ReceivedTipsListView(generics.ListAPIView):
    """
    API endpoint for users to view tips they have received.
    """
    serializer_class = TipDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Prefetch related tipper and tippee.
        return Tip.objects.filter(tippee=self.request.user).select_related('tipper', 'tippee').order_by('-timestamp')
