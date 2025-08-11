#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migration vers le Design Moderne
Migre automatiquement les templates vers le design system moderne
"""

import os
import re
from pathlib import Path
import shutil

class TemplateMigrator:
    """Migrateur de templates vers le design moderne"""
    
    def __init__(self):
        self.replacements = {
            # Template de base
            'extends "base.html"': 'extends "base_modern.html"',
            
            # Classes Bootstrap vers classes modernes
            'col-md-12': 'w-full',
            'col-md-6': 'md:w-1/2',
            'col-md-4': 'md:w-1/3',
            'col-md-3': 'md:w-1/4',
            'col-lg-8': 'lg:w-2/3',
            'col-lg-4': 'lg:w-1/3',
            
            # Espacement Bootstrap vers classes modernes
            'mb-4': 'mb-6',
            'mb-3': 'mb-4',
            'mb-2': 'mb-3',
            'mt-4': 'mt-6',
            'mt-3': 'mt-4',
            'me-2': 'mr-2',
            'ms-2': 'ml-2',
            
            # Classes de formulaires
            'form-select': 'form-control form-select',
            'form-range': 'form-control',
            'form-check': 'checkbox-card',
            'form-check-input': '',
            'form-check-label': 'checkbox-label',
            
            # Boutons
            'btn-outline-primary': 'btn btn-secondary',
            'btn-outline-secondary': 'btn btn-secondary',
            
            # Cartes
            'card-header': 'card-header',
            'card-body': 'card-body',
            
            # Grilles
            'row': 'grid gap-6',
            'container-fluid': 'container',
        }
        
        self.class_patterns = [
            # Remplacer les grilles Bootstrap
            (r'<div class="row">', '<div class="grid gap-6">'),
            (r'<div class="col-(\w+)-(\d+)">', self._replace_col_class),
            
            # Remplacer les classes d'espacement
            (r'\bm([btlr]?)-(\d+)\b', self._replace_spacing),
            (r'\bp([btlr]?)-(\d+)\b', self._replace_spacing),
            
            # Remplacer les classes de texte
            (r'\btext-muted\b', 'text-secondary'),
            (r'\btext-primary\b', 'text-primary'),
            (r'\btext-center\b', 'text-center'),
            
            # Remplacer les classes de display
            (r'\bd-flex\b', 'flex'),
            (r'\bd-none\b', 'hidden'),
            (r'\bd-block\b', 'block'),
        ]
    
    def _replace_col_class(self, match):
        """Remplacer les classes de colonnes Bootstrap"""
        breakpoint = match.group(1)
        size = int(match.group(2))
        
        if size == 12:
            return '<div class="w-full">'
        elif size == 6:
            return f'<div class="{breakpoint}:w-1/2">'
        elif size == 4:
            return f'<div class="{breakpoint}:w-1/3">'
        elif size == 3:
            return f'<div class="{breakpoint}:w-1/4">'
        else:
            return f'<div class="{breakpoint}:w-{size}/12">'
    
    def _replace_spacing(self, match):
        """Remplacer les classes d'espacement Bootstrap"""
        property_type = match.group(0)[0]  # m ou p
        direction = match.group(1) if match.group(1) else ''
        size = int(match.group(2))
        
        # Convertir la taille Bootstrap vers notre système
        size_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '6'}
        new_size = size_map.get(size, str(size))
        
        # Convertir la direction
        direction_map = {'t': 't', 'b': 'b', 'l': 'l', 'r': 'r', '': ''}
        new_direction = direction_map.get(direction, direction)
        
        return f"{property_type}{new_direction}-{new_size}"
    
    def migrate_template(self, template_path):
        """Migrer un template vers le design moderne"""
        print(f"🔄 Migration de {template_path.name}")
        
        # Lire le contenu
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Sauvegarder l'original
        backup_path = template_path.with_suffix('.html.backup')
        shutil.copy2(template_path, backup_path)
        print(f"  💾 Sauvegarde créée: {backup_path.name}")
        
        # Appliquer les remplacements simples
        for old, new in self.replacements.items():
            if old in content:
                content = content.replace(old, new)
                print(f"  ✅ Remplacé: {old} → {new}")
        
        # Appliquer les remplacements par regex
        for pattern, replacement in self.class_patterns:
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    print(f"  ✅ Pattern remplacé: {pattern}")
        
        # Ajouter les styles spécifiques si nécessaire
        if not '{% block extra_head %}' in content and 'extends "base_modern.html"' in content:
            # Ajouter un bloc extra_head vide
            insert_pos = content.find('{% block content %}')
            if insert_pos > 0:
                extra_head = '\n{% block extra_head %}{% endblock %}\n\n'
                content = content[:insert_pos] + extra_head + content[insert_pos:]
                print("  ✅ Bloc extra_head ajouté")
        
        # Moderniser la structure si c'est une page simple
        if '<div class="row">' in content and 'container' not in content:
            # Envelopper dans un container
            content_start = content.find('{% block content %}')
            content_end = content.find('{% endblock %}', content_start)
            
            if content_start > 0 and content_end > 0:
                old_content = content[content_start:content_end]
                new_content = old_content.replace(
                    '{% block content %}',
                    '{% block content %}\n<div class="container">'
                ).replace(
                    '{% endblock %}',
                    '</div>\n{% endblock %}'
                )
                content = content[:content_start] + new_content + content[content_end:]
                print("  ✅ Container ajouté")
        
        # Écrire le nouveau contenu
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Migration terminée")
        return True
    
    def migrate_all_templates(self):
        """Migrer tous les templates"""
        templates_dir = Path("templates")
        
        if not templates_dir.exists():
            print("❌ Répertoire templates non trouvé")
            return False
        
        # Trouver les templates à migrer
        templates_to_migrate = []
        
        for template_file in templates_dir.glob("*.html"):
            if template_file.name.startswith('base'):
                continue  # Ignorer les templates de base
            
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'extends "base.html"' in content:
                templates_to_migrate.append(template_file)
        
        if not templates_to_migrate:
            print("✅ Aucun template à migrer - tous utilisent déjà le design moderne")
            return True
        
        print(f"🔍 {len(templates_to_migrate)} template(s) à migrer:")
        for template in templates_to_migrate:
            print(f"  • {template.name}")
        
        # Demander confirmation
        response = input("\nContinuer la migration ? (o/N): ").strip().lower()
        if response not in ['o', 'oui', 'y', 'yes']:
            print("❌ Migration annulée")
            return False
        
        # Migrer chaque template
        success_count = 0
        for template in templates_to_migrate:
            try:
                if self.migrate_template(template):
                    success_count += 1
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
        
        print(f"\n📊 Migration terminée: {success_count}/{len(templates_to_migrate)} réussies")
        
        if success_count == len(templates_to_migrate):
            print("🎉 Toutes les migrations ont réussi!")
            print("💡 Conseil: Testez l'interface pour vérifier que tout fonctionne")
            return True
        else:
            print("⚠️ Certaines migrations ont échoué")
            print("🔧 Vérifiez les fichiers de sauvegarde (.backup) si nécessaire")
            return False

def main():
    """Fonction principale"""
    print("🚀 MIGRATION VERS LE DESIGN MODERNE")
    print("=" * 50)
    
    # Changer vers le répertoire webapp si nécessaire
    if not Path("templates").exists():
        if Path("webapp/templates").exists():
            os.chdir("webapp")
        else:
            print("❌ Répertoire templates non trouvé")
            return False
    
    # Créer le migrateur
    migrator = TemplateMigrator()
    
    # Lancer la migration
    success = migrator.migrate_all_templates()
    
    if success:
        print("\n✅ MIGRATION TERMINÉE AVEC SUCCÈS!")
        print("🎨 Toutes les pages utilisent maintenant le design moderne")
        print("🔍 Lancez check_styling_consistency.py pour vérifier")
    else:
        print("\n❌ MIGRATION INCOMPLÈTE")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
