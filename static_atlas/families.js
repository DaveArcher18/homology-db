/* Sourced ordinary family rules. All unbounded integers remain decimal BigInts. */
(function (root) {
  'use strict';
  const VERSION = '1';
  const FAMILIES = ['sphere', 'real_projective_space', 'complex_projective_space'];
  const COEFFICIENTS = ['Z', 'Q', 'F2', 'F3', 'F5', 'F7', 'F11'];
  function integer(value, name) {
    if (typeof value === 'number' && !Number.isSafeInteger(value)) throw new Error(`${name} must be an exact nonnegative integer`);
    if (!/^(0|[1-9][0-9]*)$/.test(String(value))) throw new Error(`${name} must be a nonnegative decimal integer`);
    return BigInt(value);
  }
  function bounded(value, max, name) {
    if (!Number.isInteger(value) || value < 1 || value > max) throw new Error(`${name} must be between 1 and ${max}`);
    return value;
  }
  const coefficientTex = c => c === 'Z' ? '\\mathbb{Z}' : c === 'Q' ? '\\mathbb{Q}' : `\\mathbb{F}_{${c.slice(1)}}`;
  const power = (letter, i) => i === 0n ? '1' : i === 1n ? letter : `${letter}^{${i}}`;
  function group(c, rank, torsion = []) {
    const base = coefficientTex(c);
    const parts = [];
    if (rank) parts.push(rank === 1n ? base : `${base}^{${rank}}`);
    torsion.forEach(order => parts.push(`\\mathbb{Z}/${order}\\mathbb{Z}`));
    return {tex: parts.join(' \\oplus ') || '0', free_rank: String(rank), torsion_orders: torsion};
  }
  function evaluate(family, nValue, coefficient, options = {}) {
    if (!FAMILIES.includes(family)) throw new Error('Unknown family');
    if (!COEFFICIENTS.includes(coefficient)) throw new Error('Unsupported coefficient');
    const n = integer(nValue, 'n');
    const start = integer(options.start ?? '0', 'start');
    const count = bounded(options.count ?? 9, 100, 'count');
    const requestedGeneratorStart = integer(options.generatorStart ?? '0', 'generatorStart');
    const generatorCount = bounded(options.generatorCount ?? 12, 12, 'generatorCount');
    const integral = coefficient === 'Z';
    const mod2 = coefficient === 'F2';
    const sphere = family === 'sphere';
    const cp = family === 'complex_projective_space';
    const rp = family === 'real_projective_space';
    const dim = cp ? 2n * n : n;
    const scalar = coefficientTex(coefficient);
    function homology(d) {
      if (d === 0n) return group(coefficient, sphere && n === 0n ? 2n : 1n);
      if (d > dim) return group(coefficient, 0n);
      if (sphere) return group(coefficient, d === n ? 1n : 0n);
      if (cp) return group(coefficient, d % 2n === 0n ? 1n : 0n);
      if (mod2) return group(coefficient, 1n);
      if (d === n && n % 2n === 1n) return group(coefficient, 1n);
      return integral && d % 2n === 1n ? group(coefficient, 0n, ['2']) : group(coefficient, 0n);
    }
    function cohomology(d) {
      if (!rp || !integral || d === 0n || d > n) return homology(d);
      if (d === n && n % 2n === 1n) return group(coefficient, 1n);
      return d % 2n === 0n ? group(coefficient, 0n, ['2']) : group(coefficient, 0n);
    }
    let total;
    if (sphere) total = 2n;
    else if (cp) total = n + 1n;
    else if (mod2) total = n + 1n;
    else if (integral) total = n / 2n + 1n + n % 2n;
    else total = 1n + n % 2n;
    function generator(index) {
      if (index < 0n || index >= total) throw new Error('Generator index outside the additive generating set');
      if (index === 0n) return {id:'1', tex:'1', degree:'0', order:null};
      if (sphere) return {id: n === 0n ? 'e' : 'x', tex:n === 0n ? 'e' : 'x', degree:String(n), order:null};
      if (cp) return {id:`u${index}`,tex:power('u',index),degree:String(2n*index),order:null};
      if (mod2) return {id:`a${index}`,tex:power('a',index),degree:String(index),order:null};
      if (integral && index <= n/2n) return {id:`a${index}`,tex:power('a',index),degree:String(2n*index),order:'2'};
      return {id:'b',tex:'b',degree:String(n),order:null};
    }
    function product(i,j) {
      if (i === 0n) return generator(j).tex;
      if (j === 0n) return generator(i).tex;
      if (sphere) return n === 0n ? 'e' : '0';
      if (cp || mod2) return i+j <= n ? generator(i+j).tex : '0';
      if (integral && i <= n/2n && j <= n/2n && i+j <= n/2n) return generator(i+j).tex;
      return '0';
    }
    const gStart = total <= 12n ? 0n : requestedGeneratorStart < total ? requestedGeneratorStart : total-1n;
    const gCount = total <= 12n ? Number(total) : Math.min(generatorCount, Number(total-gStart > 12n ? 12n : total-gStart));
    const generators = Array.from({length:gCount},(_,i)=>generator(gStart+BigInt(i)));
    const multiplication = generators.map((_,i)=>generators.map((__,j)=>product(gStart+BigInt(i),gStart+BigInt(j))));
    let h, c, ring, multiplicationRule;
    const notes = ['Ordinary unreduced homology and cohomology; all degrees outside the stated support vanish.'];
    if (sphere) {
      h = n === 0n ? `${scalar}^{2} \\text{ in degree }0` : `${scalar} \\text{ in degrees }0,${n}`;
      c = h;
      ring = n === 0n ? `${scalar}[e]/(e^2-e),\\quad |e|=0` : `${scalar}[x]/(x^2),\\quad |x|=${n}`;
      multiplicationRule = n === 0n ? '1z=z1=z; e²=e. The unit is (1,1), and e=(1,0) in the product ring.' : '1z=z1=z; x²=0.';
    } else if (cp) {
      h = `${scalar} \\text{ in degrees }2j,\\quad 0\\leq j\\leq ${n}`;
      c = h;
      ring = `${scalar}[u]/(u^{${n+1n}}),\\quad |u|=2`;
      multiplicationRule = `u^i · u^j = u^(i+j) when i+j ≤ ${n}; zero otherwise. u^0=1.`;
    } else if (mod2) {
      h = `${scalar} \\text{ in every degree }0\\leq d\\leq ${n}`;
      c = h;
      ring = `${scalar}[a]/(a^{${n+1n}}),\\quad |a|=1`;
      multiplicationRule = `a^i · a^j = a^(i+j) when i+j ≤ ${n}; zero otherwise. a^0=1.`;
    } else if (integral) {
      h = '\\mathbb{Z}\\text{ in degree }0;\\quad \\mathbb{Z}/2\\mathbb{Z}\\text{ in odd }d,\\ 0\\lt d\\lt n;\\quad \\mathbb{Z}\\text{ in }d=n\\text{ if }n\\text{ is odd}';
      c = '\\mathbb{Z}\\text{ in degree }0;\\quad \\mathbb{Z}/2\\mathbb{Z}\\text{ in even }d,\\ 0\\lt d\\leq n;\\quad \\mathbb{Z}\\text{ in }d=n\\text{ if }n\\text{ is odd}';
      if (n === 0n) ring = '\\mathbb{Z}';
      else if (n === 1n) ring = '\\mathbb{Z}[b]/(b^2),\\quad |b|=1';
      else if (n % 2n === 0n) ring = `\\mathbb{Z}[a]/(2a,a^{${n/2n+1n}}),\\quad |a|=2`;
      else ring = `\\mathbb{Z}[a,b]/(2a,a^{${n/2n+1n}},ab,b^2),\\quad |a|=2,\\ |b|=${n}`;
      multiplicationRule = n === 0n ? 'Only scalar multiplication in degree 0.' : n === 1n ? '1 is the unit; the free degree-1 class b satisfies b²=0.' : `1 is the unit. Positive powers a^i, 1 ≤ i ≤ ${n/2n}, have order 2; a^i · a^j = a^(i+j) for i+j ≤ ${n/2n}, and zero otherwise. When n is odd the free top class b has zero product with every positive-degree class.`;
      notes.push('Integral torsion occurs in different degrees in homology and cohomology, by the universal coefficient theorem.');
    } else {
      h = `${scalar}\\text{ in degree }0${n%2n ? `\\text{ and degree }${n}` : ''}`;
      c = h;
      ring = n%2n ? `${scalar}[b]/(b^2),\\quad |b|=${n}` : scalar;
      multiplicationRule = n%2n ? '1 is the unit; b²=0.' : 'Only scalar multiplication in degree 0.';
    }
    const coverage = () => ({kind:'complete_all_degrees',text:'Complete in all degrees by the cited family rule; the displayed window is not a knowledge bound.'});
    return {family,n:String(n),coefficient,coefficient_tex:scalar,dimension:String(dim),name_tex:sphere?`S^{${n}}`:cp?`\\mathbb{CP}^{${n}}`:`\\mathbb{RP}^{${n}}`,
      rule_id:`ordinary-${family}`,rule_version:VERSION,
      rows:Array.from({length:count},(_,i)=>{const d=start+BigInt(i);return {degree:String(d),homology:homology(d),cohomology:cohomology(d)};}),
      formulas:{homology:h,cohomology:c,ring,multiplication:multiplicationRule,notes},
      coverage:{homology:coverage(),cohomology:coverage(),multiplication:coverage()},
      generators,generator_total:String(total),generator_start:String(gStart),multiplication,
      display:{start:String(start),count,generator_start:String(gStart),generator_count:gCount,multiplication_complete:BigInt(gCount)===total},
    };
  }
  root.AtlasFamilies = Object.freeze({evaluate,coefficientTex,version:VERSION,families:FAMILIES,coefficients:COEFFICIENTS});
  if (typeof module !== 'undefined' && module.exports) module.exports = root.AtlasFamilies;
})(globalThis);
