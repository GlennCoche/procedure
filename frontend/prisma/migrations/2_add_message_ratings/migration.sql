-- Migration: Ajouter table message_ratings pour le feedback et l'auto-learning

-- CreateTable
CREATE TABLE "message_ratings" (
    "id" SERIAL NOT NULL,
    "message_id" INTEGER NOT NULL,
    "rating" VARCHAR(10) NOT NULL,
    "feedback" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "message_ratings_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "message_ratings_message_id_idx" ON "message_ratings"("message_id");

-- CreateIndex
CREATE INDEX "message_ratings_rating_idx" ON "message_ratings"("rating");

-- AddForeignKey
ALTER TABLE "message_ratings" ADD CONSTRAINT "message_ratings_message_id_fkey" FOREIGN KEY ("message_id") REFERENCES "chat_messages"("id") ON DELETE CASCADE ON UPDATE CASCADE;
