from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import translation
from .models import LabourEntry
from .forms import LabourEntryForm, SignUpForm, LoginForm
from datetime import datetime, timedelta
import calendar
import json

def set_language(request):
    """Set user's preferred language - Simplified version"""
    if request.method == 'POST':
        lang = request.POST.get('language')
        # Store language preference in session
        request.session['language'] = lang
        messages.success(request, 'Language updated successfully!')
    return redirect(request.META.get('HTTP_REFERER', '/'))

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('खाते यशस्वीरित्या तयार झाले! चौगुले फार्ममध्ये स्वागत आहे.'))
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'labour/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _('चौगुले फार्ममध्ये आपले स्वागत आहे!'))
                return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'labour/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, _('आपण लॉगआउट केले आहे.'))
    return redirect('login')

@login_required
def dashboard(request):
    user_entries = LabourEntry.objects.filter(user=request.user)
    today = timezone.now().date()
    
    # Today's entries with day color
    today_entries = user_entries.filter(date=today)
    today_total = today_entries.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # This month's entries
    first_day_of_month = today.replace(day=1)
    month_entries = user_entries.filter(date__gte=first_day_of_month)
    month_total = month_entries.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Total labour count
    total_labour = user_entries.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Recent entries
    recent_entries = user_entries[:10]
    
    # Get day color based on weekday
    weekday_colors = {
        0: '#E3F2FD',  # Monday - Light Blue
        1: '#F3E5F5',  # Tuesday - Light Purple
        2: '#E8F5E9',  # Wednesday - Light Green
        3: '#FFF3E0',  # Thursday - Light Orange
        4: '#FFEBEE',  # Friday - Light Red
        5: '#E0F7FA',  # Saturday - Light Cyan
        6: '#FFF9C4'   # Sunday - Light Yellow
    }
    
    # Add day color to recent entries
    for entry in recent_entries:
        entry.day_color = weekday_colors.get(entry.date.weekday(), '#FFFFFF')
    
    # Pargi summary for this month
    pargi_summary = {}
    for entry in month_entries:
        pargi = entry.pargi_name or 'इतर'
        pargi_summary[pargi] = pargi_summary.get(pargi, 0) + entry.total_amount
    
    # Crop summary for this month
    crop_summary = {}
    for entry in month_entries:
        crop = entry.land_crop_name or 'इतर'
        crop_summary[crop] = crop_summary.get(crop, 0) + entry.total_amount
    
    context = {
        'today_total': today_total,
        'month_total': month_total,
        'total_labour': total_labour,
        'total_entries': user_entries.count(),
        'recent_entries': recent_entries,
        'pargi_summary': sorted(pargi_summary.items(), key=lambda x: x[1], reverse=True),
        'crop_summary': sorted(crop_summary.items(), key=lambda x: x[1], reverse=True),
        'today': today,
    }
    return render(request, 'labour/dashboard.html', context)

@login_required
def add_entry(request):
    if request.method == 'POST':
        form = LabourEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, _('मजुरीची नोंद यशस्वीरित्या जोडली!'))
            return redirect('dashboard')
    else:
        form = LabourEntryForm(initial={
            'date': timezone.now().date(),
            'in_time': timezone.now().time().replace(second=0, microsecond=0),
        })
    
    context = {
        'form': form,
    }
    return render(request, 'labour/add_entry.html', context)

@login_required
def list_entries(request):
    entries = LabourEntry.objects.filter(user=request.user)
    total_sum = entries.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Handle filters
    search_query = request.GET.get('search', '')
    filter_date = request.GET.get('date', '')
    filter_pargi = request.GET.get('pargi', '')
    filter_owner = request.GET.get('owner', '')
    filter_crop = request.GET.get('crop', '')
    
    if search_query:
        entries = entries.filter(
            Q(pargi_name__icontains=search_query) |
            Q(labour_name__icontains=search_query) |
            Q(owner_name__icontains=search_query) |
            Q(land_crop_name__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    if filter_date:
        entries = entries.filter(date=filter_date)
    
    if filter_pargi:
        entries = entries.filter(pargi_name__icontains=filter_pargi)
    
    if filter_owner:
        entries = entries.filter(owner_name__icontains=filter_owner)
    
    if filter_crop:
        entries = entries.filter(land_crop_name__icontains=filter_crop)
    
    total_sum = entries.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Get day colors for entries
    weekday_colors = {
        0: '#E3F2FD',  # Monday
        1: '#F3E5F5',  # Tuesday
        2: '#E8F5E9',  # Wednesday
        3: '#FFF3E0',  # Thursday
        4: '#FFEBEE',  # Friday
        5: '#E0F7FA',  # Saturday
        6: '#FFF9C4'   # Sunday
    }
    
    # Serialize entries for JSON response
    entries_data = []
    for entry in entries:
        entries_data.append({
            'id': entry.id,
            'date': entry.date.strftime('%Y-%m-%d'),
            'date_display': entry.date.strftime('%d/%m/%Y'),
            'day': entry.day,
            'day_marathi': entry.day_marathi,
            'day_color': weekday_colors.get(entry.date.weekday(), '#FFFFFF'),
            'in_time': entry.in_time.strftime('%H:%M') if entry.in_time else '',
            'out_time': entry.out_time.strftime('%H:%M') if entry.out_time else '',
            'pargi_name': entry.pargi_name,
            'labour_name': entry.labour_name,
            'quantity': entry.quantity,
            'rupees_per_head': float(entry.rupees_per_head),
            'total_amount': float(entry.total_amount),
            'land_crop_name': entry.land_crop_name or '–',
            'owner_name': entry.owner_name or '–',
            'notes': entry.notes or '',
        })
    
    context = {
        'entries': entries,
        'total_sum': total_sum,
        'search_query': search_query,
        'filter_date': filter_date,
        'filter_pargi': filter_pargi,
        'filter_owner': filter_owner,
        'filter_crop': filter_crop,
        'entry_count': entries.count(),
        'entries_json': json.dumps(entries_data),
    }
    return render(request, 'labour/list_entries.html', context)

@csrf_exempt
@login_required
def update_entry(request):
    """API endpoint to update entry via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entry_id = data.get('id')
            entry = get_object_or_404(LabourEntry, id=entry_id, user=request.user)
            
            # Update fields - convert date string to date object if needed
            if 'date' in data:
                date_str = data['date']
                # Convert from string to date object
                try:
                    if isinstance(date_str, str):
                        entry.date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    else:
                        entry.date = date_str
                except:
                    entry.date = date_str
            
            if 'in_time' in data:
                time_str = data['in_time']
                if time_str:
                    try:
                        entry.in_time = datetime.strptime(time_str, '%H:%M').time()
                    except:
                        entry.in_time = time_str
                else:
                    entry.in_time = None
            
            if 'out_time' in data:
                time_str = data['out_time']
                if time_str:
                    try:
                        entry.out_time = datetime.strptime(time_str, '%H:%M').time()
                    except:
                        entry.out_time = time_str
                else:
                    entry.out_time = None
            
            if 'pargi_name' in data:
                entry.pargi_name = data['pargi_name']
            if 'labour_name' in data:
                entry.labour_name = data['labour_name']
            if 'quantity' in data:
                entry.quantity = int(data['quantity'])
            if 'rupees_per_head' in data:
                entry.rupees_per_head = float(data['rupees_per_head'])
            if 'land_crop_name' in data:
                entry.land_crop_name = data['land_crop_name'] if data['land_crop_name'] != '–' else ''
            if 'owner_name' in data:
                entry.owner_name = data['owner_name'] if data['owner_name'] != '–' else ''
            if 'notes' in data:
                entry.notes = data['notes']
            
            # Save will automatically calculate day and total
            entry.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Entry updated successfully!',
                'entry': {
                    'id': entry.id,
                    'date': entry.date.strftime('%Y-%m-%d'),
                    'date_display': entry.date.strftime('%d/%m/%Y'),
                    'day': entry.day,
                    'day_marathi': entry.day_marathi,
                    'in_time': entry.in_time.strftime('%H:%M') if entry.in_time else '',
                    'out_time': entry.out_time.strftime('%H:%M') if entry.out_time else '',
                    'pargi_name': entry.pargi_name,
                    'labour_name': entry.labour_name,
                    'quantity': entry.quantity,
                    'rupees_per_head': float(entry.rupees_per_head),
                    'total_amount': float(entry.total_amount),
                    'land_crop_name': entry.land_crop_name or '–',
                    'owner_name': entry.owner_name or '–',
                    'notes': entry.notes or '',
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def edit_entry(request, pk):
    entry = get_object_or_404(LabourEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = LabourEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, _('नोंद यशस्वीरित्या अद्यतनित केली!'))
            return redirect('list_entries')
    else:
        form = LabourEntryForm(instance=entry)
    
    context = {
        'form': form,
        'entry': entry,
    }
    return render(request, 'labour/edit_entry.html', context)

@login_required
def delete_entry(request, pk):
    entry = get_object_or_404(LabourEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, _('नोंद यशस्वीरित्या हटवली!'))
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)

@login_required
def get_calculate_total(request):
    """API endpoint to calculate total amount"""
    if request.method == 'GET':
        quantity = request.GET.get('quantity', 0)
        rupees = request.GET.get('rupees', 0)
        try:
            total = float(quantity) * float(rupees)
            return JsonResponse({'total': total})
        except:
            return JsonResponse({'total': 0})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def export_csv(request):
    """Export entries to CSV"""
    import csv
    from django.http import HttpResponse
    
    entries = LabourEntry.objects.filter(user=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="chaugule_farm_export_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Day', 'Day (Marathi)', 'In Time', 'Out Time', 'Pargi Name', 
                     'Labour Name', 'Quantity', 'Rate/Head', 'Total', 'Crop', 'Owner', 'Notes'])
    
    for entry in entries:
        writer.writerow([
            entry.id, entry.date, entry.day, entry.day_marathi, entry.in_time, entry.out_time or '',
            entry.pargi_name, entry.labour_name, entry.quantity, entry.rupees_per_head,
            entry.total_amount, entry.land_crop_name or '', entry.owner_name or '', entry.notes or ''
        ])
    
    return response

@login_required
def reports(request):
    return render(request, 'labour/reports.html')

@login_required
def get_reports_data(request):
    """API endpoint to get reports data"""
    report_type = request.GET.get('type', 'daily')
    month = request.GET.get('month', '')
    
    entries = LabourEntry.objects.filter(user=request.user)
    
    if month:
        entries = entries.filter(date__startswith=month)
    
    if not entries:
        return JsonResponse({'data': [], 'grand_total': 0, 'grand_quantity': 0})
    
    groups = {}
    
    if report_type == 'daily':
        for entry in entries:
            date_str = entry.date.strftime('%Y-%m-%d')
            if date_str not in groups:
                groups[date_str] = []
            groups[date_str].append(entry)
    
    elif report_type == 'monthly':
        for entry in entries:
            month_str = entry.date.strftime('%Y-%m')
            if month_str not in groups:
                groups[month_str] = []
            groups[month_str].append(entry)
    
    elif report_type == 'pargi':
        for entry in entries:
            pargi = entry.pargi_name or 'Unknown'
            if pargi not in groups:
                groups[pargi] = []
            groups[pargi].append(entry)
    
    elif report_type == 'owner':
        for entry in entries:
            owner = entry.owner_name or 'Unknown'
            if owner not in groups:
                groups[owner] = []
            groups[owner].append(entry)
    
    elif report_type == 'crop':
        for entry in entries:
            crop = entry.land_crop_name or 'Unspecified'
            if crop not in groups:
                groups[crop] = []
            groups[crop].append(entry)
    
    # Prepare data for JSON
    report_data = []
    grand_total = 0
    grand_quantity = 0
    
    for key, entry_list in sorted(groups.items(), reverse=True):
        subtotal = sum(e.total_amount for e in entry_list)
        sub_qty = sum(e.quantity for e in entry_list)
        grand_total += subtotal
        grand_quantity += sub_qty
        
        entries_data = []
        for e in entry_list:
            entries_data.append({
                'date': e.date.strftime('%d/%m/%Y'),
                'day': e.day,
                'day_marathi': e.day_marathi,
                'in_time': e.in_time.strftime('%H:%M'),
                'out_time': e.out_time.strftime('%H:%M') if e.out_time else '-',
                'pargi': e.pargi_name,
                'name': e.labour_name,
                'crop': e.land_crop_name or '–',
                'quantity': e.quantity,
                'rate': float(e.rupees_per_head),
                'total': float(e.total_amount),
            })
        
        report_data.append({
            'key': key,
            'subtotal': float(subtotal),
            'quantity': sub_qty,
            'entries': entries_data,
        })
    
    return JsonResponse({
        'data': report_data,
        'grand_total': float(grand_total),
        'grand_quantity': grand_quantity,
    })