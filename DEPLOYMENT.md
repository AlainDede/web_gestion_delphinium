# Guide de déploiement - Site Delphinium

## Prérequis

- AWS CLI configuré avec les bonnes credentials
- AWS SAM CLI installé
- Node.js et npm pour le frontend
- Python 3.11 pour le backend

## Étape 1 : Configuration AWS Cognito

1. **Créer le User Pool Cognito**
   ```bash
   aws cognito-idp create-user-pool \
     --pool-name delphinium-users \
     --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true}" \
     --auto-verified-attributes email \
     --username-attributes email
   ```
   Notez le `UserPoolId` retourné.

2. **Créer le App Client**
   ```bash
   aws cognito-idp create-user-pool-client \
     --user-pool-id <USER_POOL_ID> \
     --client-name delphinium-web \
     --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
     --generate-secret false
   ```
   Notez le `ClientId` retourné.

3. **Créer les groupes d'utilisateurs**
   ```bash
   aws cognito-idp create-group --user-pool-id <USER_POOL_ID> --group-name superadmin
   aws cognito-idp create-group --user-pool-id <USER_POOL_ID> --group-name admin
   aws cognito-idp create-group --user-pool-id <USER_POOL_ID> --group-name user
   aws cognito-idp create-group --user-pool-id <USER_POOL_ID> --group-name service
   ```

## Étape 2 : Déploiement du Backend

1. **Se placer dans le dossier backend**
   ```bash
   cd backend
   ```

2. **Build et déploiement avec SAM**
   ```bash
   sam build
   sam deploy --guided --parameter-overrides CognitoUserPoolId=<USER_POOL_ID> CognitoClientId=<CLIENT_ID>
   ```

3. **Récupérer l'URL de l'API Gateway**
   Après le déploiement, notez l'URL de l'API affichée dans les outputs.

## Étape 3 : Configuration du Frontend

1. **Mettre à jour l'URL de l'API dans le frontend**
   
   Éditer `frontend/src/components/Login.js` et remplacer `YOUR_API_GATEWAY_URL` par l'URL obtenue à l'étape 2.

2. **Installer les dépendances**
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   ```

3. **Lancer le serveur de développement**
   ```bash
   npm start
   ```

4. **Build pour production**
   ```bash
   npm run build
   ```

## Étape 4 : Déploiement du Frontend sur S3

1. **Créer un bucket S3 pour le frontend**
   ```bash
   aws s3 mb s3://delphinium-frontend
   aws s3 website s3://delphinium-frontend --index-document index.html
   ```

2. **Configurer le bucket pour le hosting web**
   ```bash
   aws s3api put-bucket-policy --bucket delphinium-frontend --policy file://bucket-policy.json
   ```

3. **Déployer le frontend**
   ```bash
   cd frontend
   npm run build
   aws s3 sync build/ s3://delphinium-frontend/
   ```

## Étape 5 : Créer les premiers utilisateurs

```bash
# Créer un superadmin
aws cognito-idp admin-create-user \
  --user-pool-id <USER_POOL_ID> \
  --username admin@delphinium.be \
  --user-attributes Name=email,Value=admin@delphinium.be \
  --temporary-password TempPass123!

# Ajouter au groupe superadmin
aws cognito-idp admin-add-user-to-group \
  --user-pool-id <USER_POOL_ID> \
  --username admin@delphinium.be \
  --group-name superadmin
```

## Configuration CloudFront (Optionnel mais recommandé)

Pour améliorer les performances et ajouter HTTPS :

1. Créer une distribution CloudFront pointant vers le bucket S3
2. Configurer un certificat SSL/TLS avec ACM
3. Configurer le domaine personnalisé

## Surveillance et Logs

- Logs CloudWatch : Tous les logs Lambda sont automatiquement envoyés vers CloudWatch
- Métriques API Gateway : Disponibles dans la console AWS
- Alarms CloudWatch : À configurer selon les besoins

## Coûts estimés

Avec l'architecture serverless proposée :
- AWS Cognito : Gratuit jusqu'à 50 000 MAU
- Lambda : Gratuit jusqu'à 1M de requêtes/mois
- DynamoDB : Mode PAY_PER_REQUEST (facturation à l'usage)
- S3 : Quelques euros/mois pour le stockage et les requêtes
- API Gateway : ~3.50€/million de requêtes

**Estimation mensuelle** : 5-20€ pour une copropriété de taille moyenne

