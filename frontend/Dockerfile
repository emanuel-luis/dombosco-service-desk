# Etapa de build
FROM node:18-alpine AS build

WORKDIR /app

# Copia os arquivos de dependências
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia todo o código do aplicativo
COPY . .

# Compila o aplicativo
RUN npm run build

# Etapa de runtime
FROM node:18-alpine AS runtime

WORKDIR /app

# Copia apenas as dependências de produção
COPY package*.json ./
RUN npm install --only=production

# Copia os arquivos construídos da etapa anterior
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public

EXPOSE 3000

# Define o comando para iniciar o aplicativo
CMD ["npm", "start"]