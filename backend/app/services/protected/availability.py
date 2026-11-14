from app.models.mixins import utcnow


def actions(p, uid):
    if uid not in (p.escrow.buyer_id, p.escrow.seller_id):
        return []
    if p.rules['release'] == 'delivery_code':
        return ['dispute'] if p.escrow.status == 'funded' else []
    client = uid == p.escrow.buyer_id
    terminal = p.state in ['completed', 'cancelled', 'disputed']
    result = []
    if p.state == 'awaiting_acceptance' and utcnow() < (p.booking_start or p.deadline_at):
        if not (p.client_accepted if client else p.provider_accepted):
            result.append('accept')
    if client and p.state == 'accepted' and utcnow() < (p.booking_start or p.deadline_at):
        result.append('fund')
    if p.category == 'booking':
        if p.state in ['funded', 'service_confirmed'] and utcnow() >= p.booking_end:
            if not (p.client_confirmed_at if client else p.provider_confirmed_at):
                result.append('confirm')
    elif p.state in ['funded', 'submitted', 'revision_requested']:
        if client and p.state == 'submitted':
            result.extend(['approve', 'revise'])
        elif not client:
            result.append('submit')
    if not terminal:
        if not p.extension or p.extension['status'] != 'pending':
            result.append('request-extension')
        elif uid != p.extension['requested_by']:
            result.append('decide-extension')
        if not p.cancellation or p.cancellation['status'] != 'pending':
            if p.category != 'booking' or (utcnow() < p.booking_end and not
                    p.client_confirmed_at and not p.provider_confirmed_at):
                result.append('cancel')
        elif uid != p.cancellation['requested_by']:
            result.append('decide-cancel')
    if p.escrow.status == 'funded':
        result.append('dispute')
    return result
