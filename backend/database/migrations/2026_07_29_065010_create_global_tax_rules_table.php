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
        Schema::create('global_tax_rules', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('tax_code')->unique(); // e.g., IN_GST_18
            $table->string('country'); // e.g., India
            $table->string('regime'); // e.g., GST
            $table->json('components'); // e.g., [{"name": "CGST", "rate": 9}, {"name": "SGST", "rate": 9}]
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('global_tax_rules');
    }
};
