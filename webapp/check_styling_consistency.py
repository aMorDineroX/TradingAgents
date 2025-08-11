#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Vérification de la Cohérence du Styling
Vérifie que toutes les pages utilisent le design system moderne
"""

import os
import re
from pathlib import Path

def check_template_consistency():
    """Vérifier la cohérence des templates"""
    templates_dir = Path("templates")
    
    print("🎨 Vérification de la cohérence du styling")
    print("=" * 50)
    
    # Fichiers à vérifier
    template_files = list(templates_dir.glob("*.html"))
    
    results = {
        'modern_templates': [],
        'old_templates': [],
        'issues': []
    }
    
    for template_file in template_files:
        if template_file.name.startswith('base'):
            continue  # Ignorer les templates de base
            
        print(f"\n📄 Vérification de {template_file.name}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier quel template de base est utilisé
        if 'extends "base_modern.html"' in content:
            results['modern_templates'].append(template_file.name)
            print("  ✅ Utilise base_modern.html")
            
            # Vérifier les classes modernes
            modern_classes = [
                'container', 'card', 'btn', 'form-control', 
                'metric-card', 'chart-container', 'grid'
            ]
            
            found_classes = []
            for cls in modern_classes:
                if cls in content:
                    found_classes.append(cls)
            
            if found_classes:
                print(f"  ✅ Classes modernes trouvées: {', '.join(found_classes)}")
            else:
                print("  ⚠️ Peu de classes modernes détectées")
                
        elif 'extends "base.html"' in content:
            results['old_templates'].append(template_file.name)
            print("  ❌ Utilise encore base.html (ancien)")
            results['issues'].append(f"{template_file.name} utilise l'ancien template")
            
        else:
            print("  ⚠️ Template de base non détecté")
            results['issues'].append(f"{template_file.name} sans template de base clair")
        
        # Vérifier les classes Bootstrap obsolètes (exclure les classes de notre design system)
        bootstrap_classes = ['col-md-', 'col-lg-', 'me-2', 'mb-3', 'form-check', 'd-flex', 'text-muted']
        obsolete_found = []

        for cls in bootstrap_classes:
            if cls in content:
                obsolete_found.append(cls)
        
        if obsolete_found:
            print(f"  ⚠️ Classes Bootstrap obsolètes: {', '.join(obsolete_found)}")
            results['issues'].append(f"{template_file.name} contient des classes Bootstrap obsolètes")
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DE LA COHÉRENCE")
    print("=" * 50)
    
    print(f"✅ Templates modernes: {len(results['modern_templates'])}")
    for template in results['modern_templates']:
        print(f"   • {template}")
    
    print(f"\n❌ Templates anciens: {len(results['old_templates'])}")
    for template in results['old_templates']:
        print(f"   • {template}")
    
    print(f"\n⚠️ Problèmes détectés: {len(results['issues'])}")
    for issue in results['issues']:
        print(f"   • {issue}")
    
    # Recommandations
    if results['old_templates'] or results['issues']:
        print("\n🔧 RECOMMANDATIONS")
        print("-" * 30)
        
        if results['old_templates']:
            print("1. Migrer les templates suivants vers base_modern.html:")
            for template in results['old_templates']:
                print(f"   - {template}")
        
        if any('Bootstrap' in issue for issue in results['issues']):
            print("2. Remplacer les classes Bootstrap par les classes du design system moderne")
        
        print("3. Utiliser les composants standardisés (metric-card, chart-container, etc.)")
        print("4. Vérifier que toutes les pages ont le même look and feel")
    
    else:
        print("\n🎉 EXCELLENT!")
        print("Toutes les pages utilisent le design system moderne de façon cohérente.")
    
    return len(results['issues']) == 0

def check_css_consistency():
    """Vérifier la cohérence des fichiers CSS"""
    print("\n\n🎨 Vérification des fichiers CSS")
    print("=" * 50)
    
    css_dir = Path("static/css")
    css_files = list(css_dir.glob("*.css"))
    
    required_files = [
        'modern-design.css',
        'navigation.css', 
        'charts.css',
        'components.css'
    ]
    
    print("📁 Fichiers CSS requis:")
    for required_file in required_files:
        file_path = css_dir / required_file
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            print(f"  ✅ {required_file} ({size_kb:.1f}KB)")
        else:
            print(f"  ❌ {required_file} - MANQUANT")
    
    print(f"\n📊 Total: {len(css_files)} fichiers CSS trouvés")
    
    # Vérifier les variables CSS
    print("\n🔍 Vérification des variables CSS...")
    
    modern_design_file = css_dir / 'modern-design.css'
    if modern_design_file.exists():
        with open(modern_design_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Variables importantes à vérifier
        important_vars = [
            '--primary-color',
            '--bg-card',
            '--text-primary',
            '--space-4',
            '--radius-lg',
            '--transition-normal'
        ]
        
        for var in important_vars:
            if var in content:
                print(f"  ✅ {var}")
            else:
                print(f"  ❌ {var} - MANQUANT")
    
    return True

def generate_style_guide():
    """Générer un guide de style"""
    print("\n\n📖 Génération du guide de style")
    print("=" * 50)
    
    style_guide = """
# 🎨 Guide de Style TradingAgents

## Templates
- ✅ Utiliser `{% extends "base_modern.html" %}`
- ✅ Structurer avec `<div class="container">`
- ✅ Utiliser les en-têtes de section avec `.section-header`

## Composants Principaux
- 📊 Métriques: `.metric-card`, `.metrics-grid`
- 📈 Graphiques: `.chart-container`, `.chart-wrapper`
- 🃏 Cartes: `.card`, `.card-header`, `.card-body`
- 🔘 Boutons: `.btn`, `.btn-primary`, `.btn-secondary`
- 📝 Formulaires: `.form-group`, `.form-control`, `.form-label`

## Classes Utilitaires
- 🎯 Layout: `.grid`, `.flex`, `.container`
- 📏 Espacement: `.mb-4`, `.mt-6`, `.p-4`
- 🎨 Couleurs: `.text-primary`, `.bg-card`, `.border-color`
- 📱 Responsive: `.md:grid-cols-2`, `.lg:col-span-3`

## Variables CSS Importantes
- Couleurs: `--primary-color`, `--bg-card`, `--text-primary`
- Espacement: `--space-4`, `--space-6`, `--space-8`
- Bordures: `--radius-md`, `--radius-lg`, `--border-color`
- Transitions: `--transition-fast`, `--transition-normal`

## À Éviter
- ❌ Classes Bootstrap: `.col-md-`, `.me-2`, `.mb-3`
- ❌ Styles inline excessifs
- ❌ Couleurs hardcodées
- ❌ Tailles fixes non responsive
"""
    
    with open("STYLE_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(style_guide)
    
    print("✅ Guide de style généré: STYLE_GUIDE.md")

def main():
    """Fonction principale"""
    print("🔍 VÉRIFICATION DE LA COHÉRENCE DU STYLING TRADINGAGENTS")
    print("=" * 60)
    
    # Changer vers le répertoire webapp si nécessaire
    if not Path("templates").exists():
        if Path("webapp/templates").exists():
            os.chdir("webapp")
        else:
            print("❌ Répertoire templates non trouvé")
            return False
    
    # Vérifications
    templates_ok = check_template_consistency()
    css_ok = check_css_consistency()
    
    # Générer le guide de style
    generate_style_guide()
    
    # Résultat final
    print("\n" + "=" * 60)
    if templates_ok and css_ok:
        print("🎉 STYLING COHÉRENT!")
        print("✅ Toutes les pages utilisent le design system moderne")
        print("✅ Tous les fichiers CSS sont présents")
        print("✅ L'interface est prête pour la production")
    else:
        print("⚠️ INCOHÉRENCES DÉTECTÉES")
        print("🔧 Consultez les recommandations ci-dessus")
        print("📖 Référez-vous au guide de style généré")
    
    return templates_ok and css_ok

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
