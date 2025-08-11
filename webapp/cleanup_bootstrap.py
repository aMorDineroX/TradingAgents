#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Nettoyage des Classes Bootstrap Obsolètes
Remplace automatiquement toutes les classes Bootstrap par les classes modernes
"""

import os
import re
from pathlib import Path

class BootstrapCleaner:
    """Nettoyeur de classes Bootstrap obsolètes"""
    
    def __init__(self):
        # Mappings directs de classes
        self.class_replacements = {
            # Espacement Bootstrap → Classes modernes
            'mb-4': 'mb-6',
            'mb-3': 'mb-4', 
            'mb-2': 'mb-3',
            'mb-1': 'mb-2',
            'mt-4': 'mt-6',
            'mt-3': 'mt-4',
            'mt-2': 'mt-3',
            'mt-1': 'mt-2',
            'me-2': 'mr-2',
            'me-1': 'mr-1',
            'ms-2': 'ml-2',
            'ms-1': 'ml-1',
            
            # Grilles Bootstrap → Grid moderne
            'col-md-12': 'w-full',
            'col-md-6': 'md:w-1/2',
            'col-md-4': 'md:w-1/3',
            'col-md-3': 'md:w-1/4',
            'col-lg-8': 'lg:w-2/3',
            'col-lg-4': 'lg:w-1/3',
            'col-6': 'w-1/2',
            'col-4': 'w-1/3',
            'col-3': 'w-1/4',
            
            # Display Bootstrap → Classes modernes
            'd-flex': 'flex',
            'd-none': 'hidden',
            'd-block': 'block',
            'd-inline': 'inline',
            'd-inline-block': 'inline-block',
            
            # Texte Bootstrap → Classes modernes
            'text-muted': 'text-secondary',
            'text-center': 'text-center',
            'text-left': 'text-left',
            'text-right': 'text-right',
            
            # Formulaires Bootstrap → Classes modernes
            'form-check': 'checkbox-card',
            'form-check-input': '',
            'form-check-label': 'checkbox-label',
            'form-select': 'form-control form-select',
            'form-range': 'form-control',
            'form-text': 'text-xs text-muted mt-1',
            
            # Boutons Bootstrap → Classes modernes
            'btn-outline-primary': 'btn btn-secondary',
            'btn-outline-secondary': 'btn btn-secondary',
            
            # Utilitaires Bootstrap → Classes modernes
            'justify-content-between': 'justify-between',
            'justify-content-center': 'justify-center',
            'align-items-center': 'items-center',
            'flex-wrap': 'flex-wrap',
        }
        
        # Patterns regex pour remplacements complexes
        self.regex_patterns = [
            # Remplacer les grilles row/col
            (r'<div class="row">', '<div class="grid gap-6">'),
            (r'<div class="row ([^"]*)">', r'<div class="grid gap-6 \1">'),
            
            # Remplacer les colonnes avec breakpoints
            (r'col-(\w+)-(\d+)', self._replace_col_class),
            
            # Remplacer les classes d'espacement avec directions
            (r'\b([mp])([btlrxy]?)-(\d+)\b', self._replace_spacing_class),
            
            # Remplacer les classes de largeur Bootstrap
            (r'\bw-(\d+)\b', r'w-\1'),
            (r'\bh-(\d+)\b', r'h-\1'),
        ]
    
    def _replace_col_class(self, match):
        """Remplacer les classes de colonnes Bootstrap"""
        breakpoint = match.group(1)
        size = int(match.group(2))
        
        if size == 12:
            return 'w-full'
        elif size == 6:
            return f'{breakpoint}:w-1/2' if breakpoint != 'col' else 'w-1/2'
        elif size == 4:
            return f'{breakpoint}:w-1/3' if breakpoint != 'col' else 'w-1/3'
        elif size == 3:
            return f'{breakpoint}:w-1/4' if breakpoint != 'col' else 'w-1/4'
        elif size == 8:
            return f'{breakpoint}:w-2/3' if breakpoint != 'col' else 'w-2/3'
        else:
            return f'{breakpoint}:w-{size}/12' if breakpoint != 'col' else f'w-{size}/12'
    
    def _replace_spacing_class(self, match):
        """Remplacer les classes d'espacement Bootstrap"""
        property_type = match.group(1)  # m ou p
        direction = match.group(2) if match.group(2) else ''
        size = int(match.group(3))
        
        # Convertir la taille Bootstrap vers notre système
        size_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '6'}
        new_size = size_map.get(size, str(size))
        
        # Convertir la direction
        direction_map = {
            't': 't', 'b': 'b', 'l': 'l', 'r': 'r', 
            'x': 'x', 'y': 'y', '': ''
        }
        new_direction = direction_map.get(direction, direction)
        
        return f"{property_type}{new_direction}-{new_size}"
    
    def clean_file(self, file_path):
        """Nettoyer un fichier des classes Bootstrap"""
        print(f"🧹 Nettoyage de {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Appliquer les remplacements directs
        for old_class, new_class in self.class_replacements.items():
            if old_class in content:
                if new_class:  # Si la nouvelle classe n'est pas vide
                    content = content.replace(old_class, new_class)
                    changes_made.append(f"{old_class} → {new_class}")
                else:  # Supprimer la classe
                    content = re.sub(rf'\b{re.escape(old_class)}\b\s*', '', content)
                    changes_made.append(f"{old_class} → (supprimé)")
        
        # Appliquer les patterns regex
        for pattern, replacement in self.regex_patterns:
            if callable(replacement):
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    changes_made.append(f"Pattern {pattern} appliqué")
                    content = new_content
            else:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    changes_made.append(f"Pattern {pattern} → {replacement}")
        
        # Nettoyer les classes vides et espaces multiples
        content = re.sub(r'class="\s*"', '', content)  # Supprimer class vides
        content = re.sub(r'class="([^"]*?)\s+([^"]*?)"', r'class="\1 \2"', content)  # Nettoyer espaces
        content = re.sub(r'\s+', ' ', content)  # Espaces multiples
        
        # Sauvegarder si des changements ont été faits
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ {len(changes_made)} changements appliqués:")
            for change in changes_made[:5]:  # Afficher les 5 premiers
                print(f"    • {change}")
            if len(changes_made) > 5:
                print(f"    • ... et {len(changes_made) - 5} autres")
            
            return True
        else:
            print("  ℹ️ Aucun changement nécessaire")
            return False
    
    def clean_all_templates(self):
        """Nettoyer tous les templates"""
        templates_dir = Path("templates")
        
        if not templates_dir.exists():
            print("❌ Répertoire templates non trouvé")
            return False
        
        template_files = list(templates_dir.glob("*.html"))
        
        print(f"🧹 Nettoyage de {len(template_files)} fichiers template")
        print("=" * 50)
        
        cleaned_count = 0
        
        for template_file in template_files:
            if template_file.name.startswith('base'):
                continue  # Ignorer les templates de base
            
            if self.clean_file(template_file):
                cleaned_count += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Nettoyage terminé: {cleaned_count}/{len(template_files)} fichiers modifiés")
        
        if cleaned_count > 0:
            print("✅ Classes Bootstrap obsolètes supprimées")
            print("🎨 Design system moderne appliqué")
        else:
            print("✅ Tous les fichiers étaient déjà propres")
        
        return True

def main():
    """Fonction principale"""
    print("🧹 NETTOYAGE DES CLASSES BOOTSTRAP OBSOLÈTES")
    print("=" * 60)
    
    # Changer vers le répertoire webapp si nécessaire
    if not Path("templates").exists():
        if Path("webapp/templates").exists():
            os.chdir("webapp")
        else:
            print("❌ Répertoire templates non trouvé")
            return False
    
    # Créer le nettoyeur
    cleaner = BootstrapCleaner()
    
    # Demander confirmation
    print("Ce script va remplacer toutes les classes Bootstrap obsolètes")
    print("par les classes du design system moderne.")
    print()
    
    response = input("Continuer le nettoyage ? (o/N): ").strip().lower()
    if response not in ['o', 'oui', 'y', 'yes']:
        print("❌ Nettoyage annulé")
        return False
    
    # Lancer le nettoyage
    success = cleaner.clean_all_templates()
    
    if success:
        print("\n✅ NETTOYAGE TERMINÉ AVEC SUCCÈS!")
        print("🎨 Styling uniforme appliqué à toutes les pages")
        print("🔍 Lancez check_styling_consistency.py pour vérifier")
    else:
        print("\n❌ NETTOYAGE INCOMPLET")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
