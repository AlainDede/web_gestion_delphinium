# Backend Architecture

Ce dossier contient la logique serverless pour le site Delphinium, basée sur les services managés AWS :
- Authentification et gestion des rôles via Cognito (superadmin, admin, utilisateur, société de service)
- Stockage des documents sur S3
- Gestion des données (newsgroup, blog, calendrier, incidents) sur DynamoDB
- Fonctions Lambda pour chaque microservice

Structure :
- auth/ : Fonctions d’authentification et gestion des rôles
- newsgroup/ : Forum de discussion
- blog/ : Actualités
- calendar/ : Événements
- incidents/ : Gestion des incidents
- docs/ : Gestion documentaire

Toutes les fonctions sont conçues pour être déployées sur AWS Lambda et interagir avec les services managés AWS.
