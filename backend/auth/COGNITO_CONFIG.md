# Configuration AWS Cognito pour l'authentification

## Vue d'ensemble
Ce projet utilise AWS Cognito pour gérer l'authentification et les rôles des utilisateurs de la copropriété Delphinium.

## Groupes d'utilisateurs (Rôles)
Les 4 niveaux d'accès suivants doivent être créés dans Cognito :

1. **superadmin** - Accès complet à toutes les fonctionnalités
2. **admin** - Membres du conseil de copropriété (accès à la gestion d'incidents)
3. **user** - Résidents de l'immeuble (accès aux sections communes)
4. **service** - Sociétés de services (Syndic, etc.)

## Configuration Cognito User Pool

### Étapes de configuration :

1. **Créer un User Pool**
   ```bash
   aws cognito-idp create-user-pool \
     --pool-name delphinium-users \
     --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true}" \
     --auto-verified-attributes email \
     --username-attributes email
   ```

2. **Créer un App Client**
   ```bash
   aws cognito-idp create-user-pool-client \
     --user-pool-id <USER_POOL_ID> \
     --client-name delphinium-web \
     --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
     --generate-secret false
   ```

3. **Créer les groupes d'utilisateurs**
   ```bash
   aws cognito-idp create-group --user-pool-id <USER_POOL_ID> --group-name superadmin --description "Super administrateurs"
   aws cognito-idp create-group --user-pool-id <USER_POOL_ID> --group-name admin --description "Administrateurs du conseil"
   aws cognito-idp create-group --user-pool-id <USER_POOL_ID> --group-name user --description "Résidents"
   aws cognito-idp create-group --user-pool-id <USER_POOL_ID> --group-name service --description "Sociétés de services"
   ```

4. **Ajouter un utilisateur à un groupe**
   ```bash
   aws cognito-idp admin-add-user-to-group \
     --user-pool-id <USER_POOL_ID> \
     --username <USERNAME> \
     --group-name <GROUP_NAME>
   ```

## Variables d'environnement pour Lambda

Dans la configuration de votre fonction Lambda `auth/login.py`, définissez :
- `COGNITO_USER_POOL_ID` : ID du User Pool créé
- `COGNITO_CLIENT_ID` : ID du App Client créé

## Permissions IAM pour Lambda

La fonction Lambda doit avoir les permissions suivantes :
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cognito-idp:InitiateAuth",
        "cognito-idp:AdminGetUser",
        "cognito-idp:AdminListGroupsForUser"
      ],
      "Resource": "arn:aws:cognito-idp:REGION:ACCOUNT_ID:userpool/*"
    }
  ]
}
```

## Intégration Frontend

Le frontend appelle l'endpoint API Gateway qui déclenche la Lambda d'authentification.
Après authentification réussie, les tokens JWT sont stockés dans localStorage :
- `authToken` : AccessToken pour les appels API
- `idToken` : Token contenant les informations utilisateur et groupes
- `refreshToken` : Token de rafraîchissement
- `userRole` : Rôle extrait du token pour la gestion des permissions

## Sécurité

- Les mots de passe doivent avoir au moins 8 caractères avec majuscules, minuscules et chiffres
- Les tokens JWT expirent après 1 heure par défaut
- Le refresh token permet de renouveler l'accès sans redemander les identifiants

