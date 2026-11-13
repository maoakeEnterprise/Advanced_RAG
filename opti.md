# Optimisations à faire plus tard

## 1. Élaguer les dossiers exclus pendant le parcours (`CorpusLoader.load`)

**Statut :** pas prioritaire, à faire si le corpus change ou si le chargement devient lent.

### Le problème

`load()` utilise `sorted(self.path_root.rglob("*"))` : tous les fichiers sont listés, y compris
ceux de `.git`, `.venv`, `node_modules`... puis exclus un par un dans `_load_file`
via `_path_exclusion`. Sur un dépôt cloné, ça peut faire des dizaines de milliers de fichiers
listés pour rien.

### Pourquoi ce n'est pas fait maintenant

Mesure faite sur `vllm-0.10.1.zip` (archive de release, pas un dépôt cloné) :

- 2874 fichiers au total ;
- seulement **4** dans un dossier exclu.

Le gain serait invisible. Le vrai coût du loader est la lecture des fichiers gardés,
ce que l'élagage ne change pas.

**Quand le faire :** si le loader est pointé sur un dépôt cloné (avec `.git`, `.venv`...),
ou si une mesure (`time make run`) montre que le chargement est lent.

### Comment faire

Utiliser `Path.walk()` (Python 3.12+, le projet est en 3.13) à la place de `rglob`.

- `walk()` parcourt dossier par dossier et donne `(dossier, sous_dossiers, fichiers)`.
- Retirer un nom de `sous_dossiers` empêche `walk` d'y descendre.
- ⚠️ Il faut modifier la liste **sur place** : `sous_dossiers[:] = ...`,
  pas `sous_dossiers = ...` (sinon `walk` ne voit pas le changement).

Exemple sans rapport avec le projet :

```python
SKIP = {"corbeille", ".thumbnails"}

for folder, subfolders, files in root.walk():
    subfolders[:] = sorted(d for d in subfolders if d not in SKIP)
    for name in sorted(files):
        ...
```

### Points à ne pas oublier

1. **Test des dossiers :** réutiliser `_path_exclusion` sur le chemin relatif du sous-dossier
   (gère aussi `.egg-info`).
2. **Ordre stable :** trier les sous-dossiers (sur place) et les fichiers, pour garder le
   même ordre qu'avec `sorted(rglob(...))` et des résultats reproductibles d'une exécution à l'autre.
3. **`ExcludedFile` :** ajouter un seul `ExcludedFile` par dossier élagué
   (ex. `source=".venv"`, `reason="build_artifact"`), sinon ces fichiers disparaissent du rapport.
4. **Garder** l'appel à `_path_exclusion` dans `_load_file` (protection si appelé directement).
5. **Vérifier** après le changement que `load()` renvoie les mêmes fichiers gardés qu'avant.
