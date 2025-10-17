import React from 'react';

const FilterSidebar = ({ filters, setFilters }) => {
  const priceRanges = [
    { label: 'All Prices', value: [0, 10000] },
    { label: 'Under $50', value: [0, 50] },
    { label: '$50 - $100', value: [50, 100] },
    { label: '$100 - $200', value: [100, 200] },
    { label: '$200 - $500', value: [200, 500] },
    { label: '$500 - $1000', value: [500, 1000] },
    { label: 'Over $1000', value: [1000, 10000] }
  ];

  const categories = [
    { label: 'All Categories', value: '' },
    { label: 'Living Room', value: 'living' },
    { label: 'Bedroom', value: 'bedroom' },
    { label: 'Office', value: 'office' },
    { label: 'Dining', value: 'dining' },
    { label: 'Storage', value: 'storage' },
    { label: 'Outdoor', value: 'outdoor' }
  ];

  const materials = [
    { label: 'All Materials', value: '' },
    { label: 'Wood', value: 'wood' },
    { label: 'Metal', value: 'metal' },
    { label: 'Fabric', value: 'fabric' },
    { label: 'Leather', value: 'leather' },
    { label: 'Plastic', value: 'plastic' },
    { label: 'Glass', value: 'glass' }
  ];

  const brands = [
    { label: 'All Brands', value: '' },
    { label: 'IKEA', value: 'ikea' },
    { label: 'West Elm', value: 'west elm' },
    { label: 'CB2', value: 'cb2' },
    { label: 'Wayfair', value: 'wayfair' },
    { label: 'Ashley', value: 'ashley' }
  ];

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 sticky top-8">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Filters</h3>
      
      {/* Price Range */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-3">Price Range</h4>
        <div className="space-y-2">
          {priceRanges.map((range, index) => (
            <label key={index} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="priceRange"
                checked={filters.priceRange[0] === range.value[0] && filters.priceRange[1] === range.value[1]}
                onChange={() => setFilters({ ...filters, priceRange: range.value })}
                className="text-amber-600 focus:ring-amber-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">{range.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Categories */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-3">Categories</h4>
        <div className="space-y-2">
          {categories.map((category, index) => (
            <label key={index} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="category"
                checked={filters.category === category.value}
                onChange={() => setFilters({ ...filters, category: category.value })}
                className="text-amber-600 focus:ring-amber-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">{category.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Materials */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-3">Materials</h4>
        <div className="space-y-2">
          {materials.map((material, index) => (
            <label key={index} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="material"
                checked={filters.material === material.value}
                onChange={() => setFilters({ ...filters, material: material.value })}
                className="text-amber-600 focus:ring-amber-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">{material.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Brands */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-3">Brands</h4>
        <div className="space-y-2">
          {brands.map((brand, index) => (
            <label key={index} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="brand"
                checked={filters.brand === brand.value}
                onChange={() => setFilters({ ...filters, brand: brand.value })}
                className="text-amber-600 focus:ring-amber-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">{brand.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Clear Filters */}
      <button
        onClick={() => setFilters({
          category: '',
          priceRange: [0, 10000],
          material: '',
          brand: ''
        })}
        className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors"
      >
        Clear All Filters
      </button>
    </div>
  );
};

export default FilterSidebar;