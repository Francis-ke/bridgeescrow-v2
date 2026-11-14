from datetime import datetime, timedelta
from tests.conftest import auth


def test_details_track_funding_delivery_and_receipt(client, buyer, seller, admin):
    created = client.post('/api/escrows', headers=auth(buyer), json={
        'seller_account': seller['account'], 'amount': '100', 'title': 'Delivery details'})
    assert created.status_code == 201
    escrow = created.json['escrow']
    details = escrow['transaction']
    assert details['sender']['email'] == 'buyer@example.com'
    assert details['recipient']['email'] == 'seller@example.com'
    sender_number = client.get('/api/auth/me', headers=auth(buyer)).json['user']['card_number']
    recipient_number = client.get('/api/auth/me', headers=auth(seller)).json['user']['card_number']
    assert details['sender']['card_number'] == sender_number
    assert details['recipient']['card_number'] == recipient_number
    assert len(sender_number) == len(recipient_number) == 16
    assert sender_number != recipient_number
    assert details['card_last4'] is None
    assert details['payment_method'] == 'wallet'
    assert details['funded_at'] is None and details['received_at'] is None
    assert details['expected_delivery_at'] is None
    assert details['transaction_at'].endswith('+00:00')
    eid = escrow['id']
    client.put(f'/api/escrows/{eid}/contract', headers=auth(buyer), json={
        'terms': 'Deliver the agreed goods within five days.', 'delivery_days': 5})
    client.post(f'/api/escrows/{eid}/contract/sign', headers=auth(buyer))
    client.post(f'/api/escrows/{eid}/contract/sign', headers=auth(seller))
    client.post('/api/wallet/deposit', headers=auth(buyer), json={'amount': '100'})
    funded = client.post(f'/api/escrows/{eid}/fund', headers=auth(buyer))
    assert funded.status_code == 200
    details = funded.json['escrow']['transaction']
    assert datetime.fromisoformat(details['expected_delivery_at']) == (
        datetime.fromisoformat(details['funded_at']) + timedelta(days=5))
    assert 'after the buyer confirms' in details['receipt_status']
    code = client.post(f'/api/escrows/{eid}/release', headers=auth(buyer)).json['demo_code']
    released = client.post(f'/api/escrows/{eid}/confirm', headers=auth(buyer), json={'code': code})
    assert released.status_code == 200
    details = released.json['escrow']['transaction']
    assert details['received_at'] is not None
    assert details['receipt_status'] == 'Funds released to the recipient'
    assert client.get(f'/api/escrows/{eid}', headers=auth(admin)).status_code == 404
    listed = client.get('/api/escrows?direction=received', headers=auth(seller)).json
    assert listed['escrows'][0]['transaction']['received_at'] == details['received_at']
    assert listed['escrows'][0]['transaction']['sender']['card_number'] == sender_number
    assert listed['escrows'][0]['transaction']['recipient']['card_number'] == recipient_number


def test_refund_is_not_presented_as_received_money(client, buyer, seller):
    created = client.post('/api/escrows', headers=auth(buyer), json={
        'seller_account': seller['account'], 'amount': '100', 'title': 'Refund details'})
    eid = created.json['escrow']['id']
    client.post('/api/wallet/deposit', headers=auth(buyer), json={'amount': '100'})
    client.post(f'/api/escrows/{eid}/fund', headers=auth(buyer))
    refunded = client.post(f'/api/escrows/{eid}/refund', headers=auth(buyer))
    assert refunded.status_code == 200
    details = refunded.json['escrow']['transaction']
    assert details['received_at'] is None
    assert 'recipient will not receive' in details['receipt_status']
