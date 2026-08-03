<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Stancl\Tenancy\Database\Models\Tenant as BaseTenant;
use Stancl\Tenancy\Contracts\TenantWithDatabase;
use Stancl\Tenancy\Database\Concerns\HasDatabase;
use Stancl\Tenancy\Database\Concerns\HasDomains;

class Tenant extends BaseTenant implements TenantWithDatabase
{
    use HasDatabase, HasDomains, HasFactory;

    protected $fillable = [
        'id',
        'business_name',
        'address',
        'state',
        'city',
        'phone',
        'industry',
        'pan',
        'gstin',
        'financial_year_start',
        'enabled_modules'
    ];

    protected $casts = [
        'enabled_modules' => 'array',
    ];

    public static function getCustomColumns(): array
    {
        return [
            'id',
            'business_name',
            'address',
            'state',
            'city',
            'phone',
            'industry',
            'pan',
            'gstin',
            'financial_year_start',
            'enabled_modules'
        ];
    }

    public function hasModule(string $module): bool
    {
        $modules = $this->enabled_modules ?? ['core_accounting', 'inventory'];
        return in_array($module, $modules, true);
    }
}
