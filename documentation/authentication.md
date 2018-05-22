# Authentification

L'API utilise [Json Web Token (JWT)](https://jwt.io/) pour authentifier ses clients.
L'authentication utilisateur se fait via le Portail des Assos.

## Routes

Toutes les routes sont préfixées par `/auth`:

<!--
> Dans un version future, le but est de permettre au assos de choisir leur api d'authentification
`/login` : renvoie les choix de connexion
`/login/{provider}` : renvoie le lien de connexion du provider choisi 
`/logout/{provider}` : renvoie le lien de déconnexion du provider choisi 
 -->
- `/login` : renvoie le lien de connexion du Portail des Assos
- `/callback`: renvoie le JWT correspondant à l'utilisateur connecté
- `/logout`: revoke le JWT et renvoie le lien de déconnexion du portail
- `/refresh`: refresh le JWT

Portail API n'est utilisé qu'en cas de connexion, de déconnexion et d'accès à l'administration. Dans les autres requêtes où l'utilisateur est authentifié, il n'y a que JWTClient.

## Requête authentifiée avec JWT

Tout d'abord il faut récupérer le JWT.
Pour chaque requête, il faut