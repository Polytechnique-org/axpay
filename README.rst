axpay
=====

Small project intended to overview payment for AX services.


Design
------

The association provides a number of base ``Products``.
The price of such products evolves with time, as noted in ``ProductPrice`` objects.

On the other side, a member registers a ``PaymentMode`` (credit card, check, etc.);
money is then taken from his account through that payment mode, tracked in an ``Order``.

A single ``PaymentMode`` can be used throughout the years, thus generating several ``Orders``.

Each ``Order`` may be used to pay for one or more products, maybe not for the current user,
as recorded in a ``OrderItem``.
