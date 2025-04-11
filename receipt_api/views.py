from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponseBadRequest
import json
import re
from datetime import datetime
from .in_memory_store import Receipt, receipt_store
# Create your views here.
@api_view(['POST'])
def process_receipts(request):
    
    data = json.loads(request.body)
   
    # Check for required receipt fields
    required_fields = ["retailer", "purchaseDate", "purchaseTime", "items", "total"]
    for field in required_fields:
        if field not in data:
            return HttpResponseBadRequest(f"The receipt is invalid.")
    
    retailer = data.get("retailer")
    purchaseDate = data.get("purchaseDate")
    purchaseTime = data.get("purchaseTime")
    items = data.get("items")
    total = data.get("total")
    
    # Validate that items is a non-empty list.
    if not items or len(items) < 1 :
        return HttpResponseBadRequest("The receipt is invalid.")
    
    # Validate retailer pattern "^[\w\s\-\&]+$"
    retailer_pattern = re.compile(r'^[\w\s\-\&]+$')
    if not isinstance(retailer, str) or not retailer_pattern.fullmatch(retailer):
        return HttpResponseBadRequest("The receipt is invalid.")
    
    # Validate total pattern "^\d+\.\d{2}$"
    total_pattern = re.compile(r'^\d+\.\d{2}$')
    if not isinstance(total, str) or not total_pattern.fullmatch(total):
        return HttpResponseBadRequest("The receipt is invalid.")
    
    # Validate purchaseDate format YYYY-MM-DD (assuming this is the format)
    try:
        datetime.strptime(purchaseDate, "%Y-%m-%d")
    except ValueError:
        return HttpResponseBadRequest("The receipt is invalid.")
    
    # Validate purchaseTime HH:MM (24-hour format)
    try:
        datetime.strptime(purchaseTime, "%H:%M")
    except ValueError:
       return HttpResponseBadRequest("The receipt is invalid.")
    
    # Validate each item in the items list.
    short_desc_pattern = re.compile(r'^[\w\s\-]+$')
    price_pattern = re.compile(r'^\d+\.\d{2}$')
    
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            return HttpResponseBadRequest(f"The receipt is invalid.")
        # Check required item fields.
        for req in ["shortDescription", "price"]:
            if req not in item:
                return HttpResponseBadRequest(f"The receipt is invalid.")
        
        short_desc = item.get("shortDescription")
        price = item.get("price")
        
        if not isinstance(short_desc, str) or not short_desc_pattern.fullmatch(short_desc):
            return HttpResponseBadRequest(f"The receipt is invalid.")
        
        if not isinstance(price, str) or not price_pattern.fullmatch(price):
            return HttpResponseBadRequest(f"The receipt is invalid.")
    rec_obj = Receipt(
        retailer=retailer,
        purchase_date=purchaseDate,
        purchase_time=purchaseTime,
        total=float(total),
        items=items,
    )
    # If all validations pass, generate a unique receipt ID.
    receipt_id = str(rec_obj._id_counter)
    
    # Save the receipt object to the database.
    receipt_store[receipt_id] = rec_obj
    # Return the receipt ID in a JSON response.
    return JsonResponse({"id": receipt_id})

@api_view(['GET'])
def points_for_receipt(request, receipt_id):
    """
    Calculate points for a given receipt ID.
    """
    # Check if the receipt ID exists in the store.
    if str(receipt_id) not in receipt_store:
        return JsonResponse({"error": "No receipt found for that ID."}, status=404)
    
    # Calculate points based on the total amount.
    total = receipt_store[str(receipt_id)].count_points()
    
    return JsonResponse({"points": total})