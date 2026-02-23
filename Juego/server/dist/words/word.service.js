"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getRandomWordPair = exports.getActiveCategories = void 0;
var supabase_1 = require("../lib/supabase");
Object.defineProperty(exports, "getActiveCategories", { enumerable: true, get: function () { return supabase_1.getActiveCategories; } });
Object.defineProperty(exports, "getRandomWordPair", { enumerable: true, get: function () { return supabase_1.getRandomWordPair; } });
