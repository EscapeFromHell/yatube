from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    date = int(datetime.now().strftime('%Y'))
    return {
        'year': date
    }
