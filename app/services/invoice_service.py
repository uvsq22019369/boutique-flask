from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from app.models.order import Order
from app.models.order_item import OrderItem
import os
from datetime import datetime

class InvoiceService:
    """Service pour générer les factures PDF"""
    
    @staticmethod
    def generate_invoice(order_id):
        """Génère une facture PDF pour une commande"""
        order = Order.query.get(order_id)
        
        # ⭐ CHEMIN CORRIGÉ - Utiliser le chemin absolu
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        invoice_dir = os.path.join(base_dir, 'app', 'static', 'invoices')
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(invoice_dir, exist_ok=True)
        
        # Nom du fichier
        filename = f"facture_{order.order_number}.pdf"
        filepath = os.path.join(invoice_dir, filename)
        
        print(f"📄 Génération facture: {filepath}")  # Pour déboguer
        
        # Créer le PDF
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=20,
            spaceAfter=30
        )
        elements.append(Paragraph("FACTURE", title_style))
        
        # Informations de la boutique
        shop_info = f"""
        <b>MA BOUTIQUE</b><br/>
        Dakar, Sénégal<br/>
        Tel: 77 123 45 67<br/>
        Email: contact@maboutique.sn
        """
        elements.append(Paragraph(shop_info, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Informations de la facture
        invoice_info = f"""
        <b>Facture N°:</b> {order.order_number}<br/>
        <b>Date:</b> {order.created_at.strftime('%d/%m/%Y %H:%M')}<br/>
        <b>Caissier:</b> {order.user.username if order.user else 'Inconnu'}
        """
        elements.append(Paragraph(invoice_info, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Informations client
        if order.client:
            client_info = f"""
            <b>Client:</b> {order.client.full_name}<br/>
            <b>Tél:</b> {order.client.phone}
            """
            if order.client.email:
                client_info += f"<br/><b>Email:</b> {order.client.email}"
            elements.append(Paragraph(client_info, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Tableau des articles
        data = [['Description', 'Qté', 'Prix unit.', 'Total']]
        
        for item in order.items:
            data.append([
                item.product_name,
                str(item.quantity),
                f"{item.unit_price:,.0f} FCFA",
                f"{item.subtotal:,.0f} FCFA"
            ])
        
        # Ligne de total
        data.append(['', '', 'TOTAL', f"{order.total:,.0f} FCFA"])
        
        # Créer le tableau
        table = Table(data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -2), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Mode de paiement
        payment_info = f"<b>Mode de paiement:</b> {order.payment_method}"
        elements.append(Paragraph(payment_info, styles['Normal']))
        
        # Mention légale
        legal = """
        <br/><br/>
        <i>Merci de votre confiance !</i><br/>
        <small>Cette facture est générée automatiquement</small>
        """
        elements.append(Paragraph(legal, styles['Normal']))
        
        # Générer le PDF
        doc.build(elements)
        
        print(f"✅ Facture générée: {filepath}")
        return filepath