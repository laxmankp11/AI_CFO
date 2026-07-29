<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('ai_extractions', function (Blueprint $table) {
            $table->uuid('id')->primary();

            $table->foreignUuid('user_id')->nullable()->constrained()->nullOnDelete();
            $table->text('raw_transcript')->nullable();
            $table->jsonb('extracted_payload')->nullable();
            $table->decimal('aggregate_confidence', 5, 4)->nullable();
            $table->string('status')->default('Pending Clarification');
            $table->timestamps();
            $table->softDeletes();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('ai_extractions');
    }
};
