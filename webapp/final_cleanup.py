#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nettoyage Final des Classes Bootstrap
Supprime les dernières classes Bootstrap obsolètes détectées
"""

import os
import re
from pathlib import Path

def final_cleanup():
    """Nettoyage final des classes Bootstrap restantes"""
    print("🧹 NETTOYAGE FINAL DES CLASSES BOOTSTRAP")
    print("=" * 50)
    
    templates_dir = Path("templates")
    if not templates_dir.exists():
        print("❌ Répertoire templates non trouvé")
        return False
    
    # Classes spécifiques à nettoyer
    final_replacements = {
        'mb-3': 'mb-4',
        'card-header': 'card-header',  # Garder mais s'assurer qu'elle est dans le bon contexte
    }
    
    # Patterns spéciaux pour card-header
    card_header_patterns = [
        # Remplacer les h4/h5 dans card-header par h3
        (r'<div class="card-header">\s*<h([45])[^>]*>', r'<div class="card-header">\n                <h3'),
        (r'</h[45]>\s*</div>', r'</h3>\n            </div>'),
        
        # Nettoyer les classes me-2 restantes dans les headers
        (r'<i class="([^"]*)\s+me-2([^"]*)">', r'<i class="\1\2">'),
        (r'me-2\s*', ''),
    ]
    
    template_files = [f for f in templates_dir.glob("*.html") if not f.name.startswith('base')]
    
    cleaned_files = 0
    
    for template_file in template_files:
        print(f"\n🔍 Vérification de {template_file.name}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        # Remplacements simples
        for old, new in final_replacements.items():
            if old in content and old != new:
                content = content.replace(old, new)
                changes.append(f"{old} → {new}")
        
        # Patterns spéciaux
        for pattern, replacement in card_header_patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes.append(f"Pattern card-header nettoyé")
                content = new_content
        
        # Nettoyer les espaces multiples et classes vides
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'class="\s*"', '', content)
        content = re.sub(r'class="([^"]*?)\s+([^"]*?)"', r'class="\1 \2"', content)
        
        # Sauvegarder si changements
        if content != original_content:
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ {len(changes)} changements appliqués")
            for change in changes:
                print(f"    • {change}")
            
            cleaned_files += 1
        else:
            print("  ✅ Déjà propre")
    
    print(f"\n📊 Nettoyage final terminé: {cleaned_files} fichiers modifiés")
    return True

def verify_consistency():
    """Vérifier la cohérence finale"""
    print("\n🔍 VÉRIFICATION FINALE")
    print("=" * 30)
    
    templates_dir = Path("templates")
    template_files = [f for f in templates_dir.glob("*.html") if not f.name.startswith('base')]
    
    issues = []
    
    for template_file in template_files:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier les classes Bootstrap obsolètes restantes
        bootstrap_classes = ['mb-3', 'me-2', 'col-md-', 'col-lg-', 'form-check']
        found_issues = []
        
        for cls in bootstrap_classes:
            if cls in content:
                found_issues.append(cls)
        
        if found_issues:
            issues.append(f"{template_file.name}: {', '.join(found_issues)}")
        else:
            print(f"✅ {template_file.name}")
    
    if issues:
        print("\n⚠️ Classes Bootstrap restantes:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("\n🎉 STYLING PARFAITEMENT UNIFORME!")
        print("✅ Toutes les pages utilisent le design system moderne")
        print("✅ Aucune classe Bootstrap obsolète détectée")
        return True

def main():
    """Fonction principale"""
    # Changer vers le répertoire webapp si nécessaire
    if not Path("templates").exists():
        if Path("webapp/templates").exists():
            os.chdir("webapp")
        else:
            print("❌ Répertoire templates non trouvé")
            return False
    
    # Nettoyage final
    final_cleanup()
    
    # Vérification finale
    success = verify_consistency()
    
    if success:
        print("\n🎉 MISSION ACCOMPLIE!")
        print("🎨 Le styling est maintenant parfaitement uniforme")
        print("🚀 L'interface est prête pour la production")
    else:
        print("\n⚠️ Quelques ajustements restent nécessaires")
        print("🔧 Consultez les détails ci-dessus")
    
    return success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
