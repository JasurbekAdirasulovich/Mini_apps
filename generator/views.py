from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .services.ai_service import AIService

def home_view(request):
    """
    Renders the Home page where users fill in test parameters.
    """
    return render(request, 'generator/home.html')

def generate_view(request):
    """
    Handles form submission, creates prompts, contacts Gemini API,
    validates JSON and stores test structure in the session.
    Redirects to the Preview page.
    """
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        topics = request.POST.get('topics', '').strip()
        
        try:
            questions_count = int(request.POST.get('questions_count', 10))
        except ValueError:
            questions_count = 10
            
        difficulty = request.POST.get('difficulty', 'medium')
        language = request.POST.get('language', 'uz')
        ai_model = request.POST.get('ai_model', 'gemma-4-31b')

        # Simple validation
        if not subject or not topics:
            return render(request, 'generator/home.html', {
                'error': "Fan nomi va mavzular to'ldirilishi shart.",
                'subject': subject,
                'topics': topics,
                'questions_count': questions_count,
                'difficulty': difficulty,
                'language': language,
                'ai_model': ai_model
            })

        # Call AI Service
        try:
            ai_service = AIService()
            success, test_data, message = ai_service.generate_test(
                subject=subject,
                topics=topics,
                count=questions_count,
                difficulty=difficulty,
                language=language,
                model_name=ai_model
            )
        except ValueError as val_err:
            return render(request, 'generator/home.html', {
                'error': str(val_err),
                'subject': subject,
                'topics': topics,
                'questions_count': questions_count,
                'difficulty': difficulty,
                'language': language,
                'ai_model': ai_model
            })

        if success:
            request.session['test_data'] = test_data
            if message:
                request.session['warning_message'] = message
            else:
                if 'warning_message' in request.session:
                    del request.session['warning_message']
            return redirect('generator:preview')
        else:
            return render(request, 'generator/home.html', {
                'error': message or "Kutilmagan xatolik yuz berdi.",
                'subject': subject,
                'topics': topics,
                'questions_count': questions_count,
                'difficulty': difficulty,
                'language': language,
                'ai_model': ai_model
            })

    return redirect('generator:home')

def preview_view(request):
    """
    Displays the generated questions list for review.
    """
    test_data = request.session.get('test_data')
    if not test_data:
        return redirect('generator:home')
    return render(request, 'generator/preview.html', {'test_data': test_data})

from .services.shuffle_engine import ShuffleEngine

def shuffle_view(request):
    """
    Renders the options to shuffle questions/choices and generate variants.
    Processes variant generation on POST request.
    """
    test_data = request.session.get('test_data')
    if not test_data:
        return redirect('generator:home')

    if request.method == 'POST':
        shuffle_questions = request.POST.get('shuffle_questions') == 'yes'
        shuffle_options = request.POST.get('shuffle_options') == 'yes'
        
        try:
            variants_count = int(request.POST.get('variants_count', 2))
        except ValueError:
            variants_count = 2

        try:
            q_per_var = request.POST.get('questions_per_variant')
            questions_per_variant = int(q_per_var) if q_per_var else None
        except ValueError:
            questions_per_variant = None

        # Generate the variants
        variants = ShuffleEngine.generate_variants(
            original_test_data=test_data,
            shuffle_questions=shuffle_questions,
            shuffle_options=shuffle_options,
            variants_count=variants_count,
            questions_per_variant=questions_per_variant
        )
        
        # Save to session
        request.session['variants'] = variants
        return redirect('generator:export')

    return render(request, 'generator/shuffle.html', {'test_data': test_data})

def export_view(request):
    """
    Displays downloading options (DOCX, PDF, keys).
    """
    test_data = request.session.get('test_data')
    variants = request.session.get('variants')
    if not test_data or not variants:
        return redirect('generator:home')
    return render(request, 'generator/export.html', {
        'test_data': test_data,
        'variants': variants
    })

from .services.word_exporter import WordExporter
from .services.pdf_exporter import PDFExporter

def export_docx_view(request):
    """
    Generates and returns the DOCX file.
    """
    variants = request.session.get('variants')
    if not variants:
        return redirect('generator:home')
    
    # Generate DOCX
    docx_stream = WordExporter.generate_docx(variants)
    
    response = HttpResponse(
        docx_stream.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    # Sanitize filename
    subject_safe = "".join(c for c in variants.get('subject', 'test') if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"AI_Test_{subject_safe}.docx"
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def export_pdf_view(request):
    """
    Generates and returns the PDF file.
    """
    variants = request.session.get('variants')
    if not variants:
        return redirect('generator:home')
    
    # Generate PDF
    pdf_stream = PDFExporter.generate_pdf(variants)
    
    response = HttpResponse(pdf_stream.getvalue(), content_type='application/pdf')
    # Sanitize filename
    subject_safe = "".join(c for c in variants.get('subject', 'test') if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"AI_Test_{subject_safe}.pdf"
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def reset_view(request):
    """
    Clears test generator data from the session and redirects home.
    """
    if 'test_data' in request.session:
        del request.session['test_data']
    if 'variants' in request.session:
        del request.session['variants']
    return redirect('generator:home')
