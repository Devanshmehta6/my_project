from django.http import HttpResponse
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status

import os
import zipfile
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import viewsets, status
import PyPDF2

class FileOperationsViewSet(viewsets.ViewSet):
    
    def split_pdf(self, pdf_path, output_folder):
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            split_files = []
            for i in range(len(reader.pages)):
                writer = PyPDF2.PdfWriter()
                writer.add_page(reader.pages[i])

                # Save each page as a separate PDF
                output_filename = os.path.join(output_folder, f"page_{i + 1}.pdf")
                with open(output_filename, 'wb') as output_pdf:
                    writer.write(output_pdf)
                split_files.append(output_filename)
        return split_files
    
    @action(detail=False, methods=['post'])
    def split_pdf_file(self, request):
        """Endpoint to handle PDF splitting."""
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Save uploaded file temporarily
        temp_pdf_path = default_storage.save(uploaded_file.name, uploaded_file)
        temp_pdf_full_path = default_storage.path(temp_pdf_path)

        # Define output folder for split PDFs
        output_folder = os.path.join(settings.MEDIA_ROOT, "split_pdfs")
        os.makedirs(output_folder, exist_ok=True)

        try:
            # Split the PDF and create a zip file
            split_files = self.split_pdf(temp_pdf_full_path, output_folder)
            zip_filename = "split_pdfs.zip"
            zip_filepath = os.path.join(output_folder, zip_filename)
            with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                for file in split_files:
                    zipf.write(file, os.path.basename(file))
            for file in split_files:
                os.remove(file)  # Clean up individual files after zipping

            # Return the zip file as a response
            with open(zip_filepath, 'rb') as zipf:
                response = HttpResponse(zipf.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename={zip_filename}'
                return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # Clean up the zip file
            if os.path.exists(zip_filepath):
                os.remove(zip_filepath)

    # @action(detail=False, methods=['post'])
    
    
    
    # @action(detail=False, methods=['post'])
    
        
    