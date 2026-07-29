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
        Schema::create('journal_entries', function (Blueprint $table) {
            $table->uuid('id')->primary();

            $table->date('entry_date');
            $table->text('narration')->nullable();
            $table->string('status')->default('Draft'); // Draft, Posted, Voided
            $table->uuid('source_id')->nullable();
            $table->string('source_type')->nullable();
            $table->timestamps();
            $table->softDeletes();
            
            $table->index(['source_id', 'source_type']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('journal_entries');
    }
};
