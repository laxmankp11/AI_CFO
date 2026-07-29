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
        Schema::create('tenant_tax_settings', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->boolean('is_tax_registered')->default(false);
            $table->string('tax_id_number')->nullable(); // GSTIN, VAT, etc.
            $table->string('default_sales_tax_code')->nullable(); // Foreign key to global_tax_rules
            $table->string('default_purchase_tax_code')->nullable();
            $table->boolean('is_tax_inclusive')->default(false);
            $table->string('home_state')->nullable(); // Used for Place of Supply (e.g. Maharashtra)
            $table->json('ai_preferences')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('tenant_tax_settings');
    }
};
