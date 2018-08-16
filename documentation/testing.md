# Test de l'API

## Utilisation

Pour lancer les tests, utilisez `python manage.py test`.
Une fois la série de test réalisée, vous saurez quels tests ont échoués

## Développement

Les tests se trouvent dans les fichiers `tests.py` et correspondent aux classes héritant de `rest_framework.test.APITestCase`.

### CRUDViewSetTestMixin

Pour généraliser les tests de l'API, une classe `CRUDViewSetTestMixin` a été créée.

#### Utilisation

Pour l'utiliser, faire hériter la classe de test de `CRUDViewSetTestMixin` et `APITestCase` (dans cet ordre), comme ceci :
```python
class UserTypeViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = UserType
	permissions = get_permissions_from_compact({ ... })

	def _get_object_attributes(self, user=None):
		return { ... }
```

3 attributs doivent être spécifiées :
- `model` : le model correspondant à la view
- `permissions` : les permissions attendues [(voir ici)](#Permissions)

#### Permissions

Pour chaque tests, nous avons 4 utilisateurs performant les requêtes :
- `admin` : un administrateur
- `user` : un premier utilisateur lambda, ce sera lui qui possèdera les objets si possible
- `other` : un second utilisateur lambda, il tentera d'accèder aux objets de `user` 
- `public` : un utilisateur non connecté
Chaque utilisateur représente un niveau de visibilité.
Nous testons chaque action possible avec chaque niveau de visibilité afin de vérifier que nous avons bien le résultat attendu.

Les permissions sont de la forme suivante :
```python
permissions = {
	'<action>': 	{ '<user>': <is_allowed>, ... },
	...
}
```
Avec :
- `<action>` : l'action CRUD
- `<user>` : un des utilisateurs précédents
- `<is_allowed>` : `True` si l'utisateur peut effectuer l'action, sinon `False`
La permission de base est `core.tests.DEFAULT_CRUD_PERMISSIONS`.

Comme ce format est assez lourd, le helper `core.tests.get_permissions_from_compact` permet l'utilisation d'un format compact de type :
```python
permissions = get_permissions_from_compact({
	'<action>': <compact>,
	...
})
```
`<compact>` est cette fois une chaîne de charactères, chaque lettre présente passe l'action de l'utisateur dont elle est l'initiale à `True`, à partir de `DEFAULT_CRUD_PERMISSIONS`.

Par exemple `'update': ".u.a"` donne :
```python
'update': { 'public': False, 'user': True, 'other': False, 'admin': True }
```

Voici un exemple complet :
```python
permissions = get_permissions_from_compact({
	'list': 	"puoa", 	# Everyone can list
	'retrieve': "puoa", 	# Everyone can retrieve
	'create': 	"...a", 	# Only admin can create
	'update': 	"...a", 	# Only admin can update
	'delete': 	"...a", 	# Only admin can delete
})
```

#### Structure

Cette classe possède 5 tests correspondant aux 5 actions possibles sur une view API CRUD :
- `test_list_view`
- `test_retrieve_view`
- `test_create_view`
- `test_update_view`
- `test_delete_view`
Le reste des méthodes sont des helpers et peuvent être surchargés pour la plupart.
