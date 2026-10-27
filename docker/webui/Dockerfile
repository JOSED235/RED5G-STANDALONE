# WebUI de Open5GS (gestión de suscriptores) compilada desde el código fuente,
# fijada a la misma versión del núcleo instalada desde el PPA (v2.8.0).
FROM node:20-bookworm AS builder

ARG OPEN5GS_VERSION=v2.8.0
RUN git clone --depth 1 -b ${OPEN5GS_VERSION} https://github.com/open5gs/open5gs.git /src
WORKDIR /src/webui
RUN npm ci --no-audit --no-fund && npm run build

FROM node:20-bookworm-slim

COPY --from=builder /src/webui /webui
WORKDIR /webui

ENV NODE_ENV=production \
    PORT=9999 \
    DB_URI=mongodb://mongodb/open5gs

EXPOSE 9999

CMD ["npm", "run", "start"]
