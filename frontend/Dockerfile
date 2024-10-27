FROM node:18-alpine

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED 1

RUN mkdir -p .next node_modules

COPY package*.json ./

RUN npm ci

COPY . .

RUN chown -R node:node /app

USER node

RUN npx prisma generate --schema ./prisma/schema.prisma

ENTRYPOINT ["./entrypoint.sh"]
# CMD ["npm", "run", "dev"]
