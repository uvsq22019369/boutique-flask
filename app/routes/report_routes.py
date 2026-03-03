from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from app.services.report_service import ReportService
from app.utils.helpers import role_required
from datetime import datetime, timedelta
import pandas as pd
import io

report_bp = Blueprint('report', __name__, url_prefix='/rapports')

@report_bp.route('/')
@login_required
@role_required('admin', 'manager')
def index():
    """Page des rapports"""
    return render_template('reports/index.html')

@report_bp.route('/ventes')
@login_required
@role_required('admin', 'manager')
def sales_report():
    """Rapport des ventes de la boutique"""
    days = request.args.get('days', 30, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    report = ReportService.get_sales_report(
        current_user.shop_id,  # ⭐ Passer shop_id
        start_date, 
        end_date
    )
    return render_template('reports/sales.html', report=report, days=days)

@report_bp.route('/stock')
@login_required
@role_required('admin', 'manager')
def stock_report():
    """Rapport des stocks de la boutique"""
    report = ReportService.get_stock_report(current_user.shop_id)  # ⭐ Passer shop_id
    return render_template('reports/stock.html', report=report)

@report_bp.route('/mouvements')
@login_required
@role_required('admin', 'manager')
def movements_report():
    """Rapport des mouvements de la boutique"""
    days = request.args.get('days', 30, type=int)
    report = ReportService.get_movements_report(current_user.shop_id, days)  # ⭐ Passer shop_id
    return render_template('reports/movements.html', report=report, days=days)

@report_bp.route('/clients')
@login_required
@role_required('admin', 'manager')
def clients_report():
    """Rapport des clients de la boutique"""
    report = ReportService.get_client_report(current_user.shop_id)  # ⭐ Passer shop_id
    return render_template('reports/clients.html', report=report)

@report_bp.route('/export/excel/<type>')
@login_required
@role_required('admin')
def export_excel(type):
    """Export Excel des rapports"""
    if type == 'stock':
        report = ReportService.get_stock_report(current_user.shop_id)
        
        # Créer DataFrame pour les produits
        df = pd.DataFrame(report['products'])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Stock', index=False)
            
            summary_df = pd.DataFrame([
                ['Total produits', report['summary']['total_products']],
                ['Valeur totale', f"{report['summary']['total_value']:,.0f} FCFA"],
                ['Stock bas', report['summary']['low_stock_count']],
                ['Rupture', report['summary']['out_of_stock_count']]
            ], columns=['Indicateur', 'Valeur'])
            summary_df.to_excel(writer, sheet_name='Résumé', index=False)
        
        output.seek(0)
        
        filename = f"rapport_stock_{current_user.shop_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    elif type == 'ventes':
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        report = ReportService.get_sales_report(current_user.shop_id, start_date, end_date)
        
        days_df = pd.DataFrame([
            {'Date': k, 'Ventes': v['count'], 'Chiffre': v['revenue']}
            for k, v in report['sales_by_day'].items()
        ])
        
        products_df = pd.DataFrame([
            {'Produit': k, 'Quantité': v['quantity'], 'Chiffre': v['revenue']}
            for k, v in report['top_products']
        ])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame([{
                'Période': f"{report['period']['start'].strftime('%d/%m/%Y')} - {report['period']['end'].strftime('%d/%m/%Y')}",
                'Total commandes': report['summary']['total_orders'],
                'Chiffre total': report['summary']['total_revenue'],
                'Panier moyen': report['summary']['avg_order_value']
            }]).to_excel(writer, sheet_name='Résumé', index=False)
            
            days_df.to_excel(writer, sheet_name='Ventes par jour', index=False)
            products_df.to_excel(writer, sheet_name='Top produits', index=False)
        
        output.seek(0)
        
        filename = f"rapport_ventes_{current_user.shop_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    return "Type d'export non supporté", 400

@report_bp.route('/api/stats')
@login_required
def api_stats():
    """API pour les statistiques (pour les graphiques)"""
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Commandes de la boutique uniquement
    orders = Order.query.filter(
        Order.shop_id == current_user.shop_id,
        Order.created_at >= start_date,
        Order.created_at <= end_date,
        Order.status == 'paid'
    ).all()
    
    sales_data = {}
    for i in range(days):
        day = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        sales_data[day] = {'count': 0, 'revenue': 0}
    
    for order in orders:
        day = order.created_at.strftime('%Y-%m-%d')
        if day in sales_data:
            sales_data[day]['count'] += 1
            sales_data[day]['revenue'] += order.total
    
    # Top produits de la boutique
    product_sales = {}
    for order in orders:
        for item in order.items:
            if item.product_name not in product_sales:
                product_sales[item.product_name] = 0
            product_sales[item.product_name] += item.quantity
    
    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return jsonify({
        'sales': {
            'labels': list(sales_data.keys()),
            'counts': [d['count'] for d in sales_data.values()],
            'revenues': [d['revenue'] for d in sales_data.values()]
        },
        'top_products': {
            'labels': [p[0] for p in top_products],
            'data': [p[1] for p in top_products]
        }
    })