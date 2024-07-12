from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .transmitter import Transmitter
from .receiver import Receiver
from django.views.decorators.http import require_http_methods
from gbn_app.constants import Encoding
from gbn_app.encoding import Encoding
import traceback
import json

transmitter_instance = None
receiver_instance = None

def home(request):
    """Render the home page."""
    return render(request, 'home.html')

@csrf_exempt
def start_transmitter(request):
    """Start the transmitter."""
    global transmitter_instance
    if transmitter_instance is None or not transmitter_instance.running:
        try:
            transmitter_instance = Transmitter()
            transmitter_instance.start()
            return JsonResponse({'status': 'Transmitter started'})
        except Exception as e:
            error_message = f"Error starting transmitter: {str(e)}"
            stack_trace = traceback.format_exc()
            transmitter_instance.log(error_message)
            transmitter_instance.log(stack_trace)
            return JsonResponse({'status': 'Error', 'message': error_message, 'traceback': stack_trace}, status=500)
    return JsonResponse({'status': 'Transmitter already running'})

@csrf_exempt
def stop_transmitter(request):
    """Stop the transmitter."""
    global transmitter_instance
    if transmitter_instance and transmitter_instance.running:
        transmitter_instance.stop()
        transmitter_instance = None
        return JsonResponse({'status': 'Transmitter stopped'})
    return JsonResponse({'status': 'Transmitter not running'})

@csrf_exempt
def start_receiver(request):
    """Start the receiver."""
    global receiver_instance
    if receiver_instance is None or not receiver_instance.running:
        try:
            receiver_instance = Receiver()
            receiver_instance.start()
            return JsonResponse({'status': 'Receiver started'})
        except Exception as e:
            error_message = f"Error starting receiver: {str(e)}"
            stack_trace = traceback.format_exc()
            receiver_instance.log(error_message)
            receiver_instance.log(stack_trace)
            return JsonResponse({'status': 'Error', 'message': error_message, 'traceback': stack_trace}, status=500)
    return JsonResponse({'status': 'Receiver already running'})

@csrf_exempt
def stop_receiver(request):
    """Stop the receiver."""
    global receiver_instance
    if receiver_instance and receiver_instance.running:
        receiver_instance.stop()
        receiver_instance = None
        return JsonResponse({'status': 'Receiver stopped'})
    return JsonResponse({'status': 'Receiver not running'})

def get_logs(request):
    """Get logs from both transmitter and receiver."""
    transmitter_logs = transmitter_instance.get_logs() if transmitter_instance else []
    receiver_logs = receiver_instance.get_logs() if receiver_instance else []
    return JsonResponse({
        'transmitter_logs': transmitter_logs,
        'receiver_logs': receiver_logs
    })

# @csrf_exempt
# def clear_logs(request):
#     """Clear logs for both transmitter and receiver."""
#     if transmitter_instance:
#         while True:
#             try:
#                 transmitter_instance.log_queue.get()
#             except Empty:
#                 transmitter_instance.log("The log_queue is empty now")
#                 break
#         transmitter_instance.logs.clear()
#     if receiver_instance:
#         while True:
#             try:
#                 receiver_instance.log_queue.get()
#             except Empty:
#                 receiver_instance.log("The log_queue is empty now")
#                 break
#         receiver_instance.logs.clear()
#     return JsonResponse({'status': 'Logs cleared'})
@csrf_exempt
def clear_logs(request):
    """Clear logs for both transmitter and receiver."""
    if transmitter_instance:
        transmitter_instance.clear_logs()
    if receiver_instance:
        receiver_instance.clear_logs()
    return JsonResponse({'status': 'Logs cleared'})

# @csrf_exempt
# def clear_logs(request):
#     """Clear logs for both transmitter and receiver."""
#     if transmitter_instance:
#         while not transmitter_instance.log_queue.empty():
#             try:
#                 transmitter_instance.log_queue.get_nowait()
#             except queue.Empty:
#                 break
#         transmitter_instance.log("Log queue cleared")
    
#     if receiver_instance:
#         while not receiver_instance.log_queue.empty():
#             try:
#                 receiver_instance.log_queue.get_nowait()
#             except queue.Empty:
#                 break
#         receiver_instance.log("Log queue cleared")
#     return JsonResponse({'status': 'Logs cleared'})

@csrf_exempt
@require_http_methods(["POST"])
def set_encoding(request):
    try:
        data = json.loads(request.body)
        new_encoding = data.get('encoding')
        
        if not isinstance(new_encoding, str):
            return JsonResponse({'status': 'error', 'message': 'Invalid encoding format'}, status=400)
        
        new_encoding = new_encoding.upper()
        
        valid_encodings = ['PARITY', 'TWO_D_PARITY', 'CHECKSUM', 'HAMMING']
        if new_encoding not in valid_encodings:
            return JsonResponse({'status': 'error', 'message': 'Invalid encoding type'}, status=400)
        
        global ENCODING
        ENCODING = getattr(Encoding, new_encoding)
        
        return JsonResponse({'status': 'success', 'encoding': new_encoding})
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def get_status(request):
    """Get the current status of transmitter and receiver."""
    transmitter_status = 'running' if transmitter_instance and transmitter_instance.running else 'stopped'
    receiver_status = 'running' if receiver_instance and receiver_instance.running else 'stopped'
    return JsonResponse({
        'transmitter_status': transmitter_status,
        'receiver_status': receiver_status
    })
