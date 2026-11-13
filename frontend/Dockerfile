# Étape 1 : compilation Angular (mode docker => appels vers /api)
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx ng build --configuration docker

# Étape 2 : nginx sert le site et redirige /api vers le backend
FROM nginx:1.29-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/senalert/browser /usr/share/nginx/html
EXPOSE 80
