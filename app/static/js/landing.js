/* ══════════════════════════════════════════
   Foodly Landing JS – Delivery · Cochabamba
   ══════════════════════════════════════════ */

'use strict';

// ── Navbar scroll ────────────────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
});

// ── Mobile hamburger ─────────────────────────────────────────────
const hamburger = document.getElementById('hamburger');
const navMobile = document.getElementById('navMobile');
hamburger && hamburger.addEventListener('click', () => {
  navMobile.classList.toggle('open');
});
// Close mobile nav when link clicked
navMobile && navMobile.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => navMobile.classList.remove('open'));
});

// ── Toast ────────────────────────────────────────────────────────
function toast(msg, type = 'success') {
  const c = document.getElementById('toastContainer');
  if (!c) return;
  const t = document.createElement('div');
  t.className = 'toast ' + type;
  const icons = { success: 'fa-circle-check', info: 'fa-circle-info', error: 'fa-circle-xmark' };
  t.innerHTML = `<i class="fa-solid ${icons[type] || icons.success}"></i><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => t.classList.add('show'), 50);
  setTimeout(() => {
    t.classList.remove('show');
    setTimeout(() => { if (c.contains(t)) c.removeChild(t); }, 400);
  }, 3500);
}

// ── Fade-in on scroll (IntersectionObserver) ─────────────────────
const fadeEls = document.querySelectorAll('.fade-in');
if (fadeEls.length) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  fadeEls.forEach(el => io.observe(el));
}

// ── Animate counter ──────────────────────────────────────────────
function animateCounter(el, target, prefix = '', suffix = '') {
  if (!el) return;
  const duration = 1200;
  const start    = performance.now();
  const from     = 0;
  const formatted = n => prefix + (n >= 1000 ? '+' + Math.floor(n / 1000) + 'K' : '+' + n) + suffix;
  const update = (now) => {
    const elapsed = Math.min((now - start) / duration, 1);
    const eased   = 1 - Math.pow(1 - elapsed, 3);
    const value   = Math.round(from + (target - from) * eased);
    el.textContent = target >= 1000
      ? prefix + '+' + (value >= 1000 ? Math.floor(value / 1000) + 'K' : value) + suffix
      : prefix + '+' + value + suffix;
    if (elapsed < 1) requestAnimationFrame(update);
    else el.textContent = prefix + (target >= 1000 ? '+' + Math.floor(target / 1000) + 'K' : '+' + target) + suffix;
  };
  requestAnimationFrame(update);
}

// ── Load stats from API ───────────────────────────────────────────
async function loadStats() {
  try {
    const r = await fetch(LANDING_URLS.stats);
    const d = await r.json();

    // Hero stats
    animateCounter(document.getElementById('stat-restaurantes'), d.restaurantes);
    animateCounter(document.getElementById('stat-minimarkets'), d.minimarkets);
    animateCounter(document.getElementById('stat-pedidos'), d.pedidos);
    const zonasEl = document.getElementById('stat-zonas');
    if (zonasEl) zonasEl.textContent = d.zonas;

    // Stats bar
    animateCounter(document.getElementById('bar-restaurantes'), d.restaurantes);
    animateCounter(document.getElementById('bar-minimarkets'), d.minimarkets);
    animateCounter(document.getElementById('bar-productos'), d.productos || 0);
    animateCounter(document.getElementById('bar-pedidos'), d.pedidos);
  } catch (e) {
    console.warn('Stats no disponibles:', e);
  }
}

// ── CART ─────────────────────────────────────────────────────────
let cart = JSON.parse(localStorage.getItem('foodly_cart') || '[]');

function saveCart() {
  localStorage.setItem('foodly_cart', JSON.stringify(cart));
}

function updateCartBadge() {
  const badge = document.getElementById('cartBadge');
  const total = cart.reduce((sum, i) => sum + i.qty, 0);
  if (!badge) return;
  if (total > 0) {
    badge.textContent = total;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
}

function updateCartTotal() {
  const totalEl = document.getElementById('cartTotal');
  if (!totalEl) return;
  const total = cart.reduce((sum, i) => sum + i.precio * i.qty, 0);
  totalEl.textContent = 'Bs ' + total.toFixed(2);
}

function renderCartItems() {
  const cartItems = document.getElementById('cartItems');
  if (!cartItems) return;

  if (cart.length === 0) {
    cartItems.innerHTML = `
      <div class="cart-empty">
        <div class="cart-empty-icon">🛒</div>
        <p>Tu carrito está vacío</p>
      </div>`;
    return;
  }

  cartItems.innerHTML = cart.map((item, idx) => `
    <div class="cart-item" data-idx="${idx}">
      <div class="cart-item-info">
        <div class="cart-item-name">${item.nombre}</div>
        <div class="cart-item-price">Bs ${(item.precio * item.qty).toFixed(2)}</div>
      </div>
      <div class="cart-item-qty">
        <button class="cart-qty-btn" data-action="dec" data-idx="${idx}">−</button>
        <span class="cart-qty-num">${item.qty}</span>
        <button class="cart-qty-btn" data-action="inc" data-idx="${idx}">+</button>
      </div>
    </div>
  `).join('');

  // Qty button events
  cartItems.querySelectorAll('.cart-qty-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx    = parseInt(btn.dataset.idx);
      const action = btn.dataset.action;
      if (action === 'inc') {
        cart[idx].qty++;
      } else {
        cart[idx].qty--;
        if (cart[idx].qty <= 0) cart.splice(idx, 1);
      }
      saveCart();
      renderCartItems();
      updateCartBadge();
      updateCartTotal();
    });
  });
}

function openCart() {
  document.getElementById('cartSidebar').classList.add('open');
  document.getElementById('cartOverlay').classList.add('open');
  renderCartItems();
  updateCartTotal();
}

function closeCart() {
  document.getElementById('cartSidebar').classList.remove('open');
  document.getElementById('cartOverlay').classList.remove('open');
}

function addToCart(id, nombre, precio, img) {
  const existing = cart.find(i => i.id === id);
  if (existing) {
    existing.qty++;
  } else {
    cart.push({ id, nombre, precio: parseFloat(precio), img, qty: 1 });
  }
  saveCart();
  updateCartBadge();
  toast(`🛒 ${nombre} añadido al carrito`, 'success');
}

// Cart event listeners
const cartBtn  = document.getElementById('cartBtn');
const cartClose = document.getElementById('cartClose');
const cartOverlay = document.getElementById('cartOverlay');
const checkoutBtn = document.getElementById('checkoutBtn');

cartBtn     && cartBtn.addEventListener('click', openCart);
cartClose   && cartClose.addEventListener('click', closeCart);
cartOverlay && cartOverlay.addEventListener('click', closeCart);

checkoutBtn && checkoutBtn.addEventListener('click', () => {
  if (cart.length === 0) {
    toast('Tu carrito está vacío', 'info');
    return;
  }
  window.location.href = LANDING_URLS.login;
});

// Add to cart buttons (product cards)
document.querySelectorAll('[data-add-product]').forEach(btn => {
  btn.addEventListener('click', () => {
    const id     = btn.dataset.addProduct;
    const nombre = btn.dataset.nombre;
    const precio = btn.dataset.precio;
    const img    = btn.dataset.img || '';
    addToCart(id, nombre, precio, img);
  });
});

// ── Copy promo code ───────────────────────────────────────────────
document.querySelectorAll('.btn-copy').forEach(btn => {
  btn.addEventListener('click', async () => {
    const code = btn.dataset.copy;
    try {
      await navigator.clipboard.writeText(code);
      btn.textContent = '¡Copiado!';
      btn.style.background = 'var(--green)';
      toast(`Código "${code}" copiado al portapapeles`, 'success');
      setTimeout(() => {
        btn.textContent = 'Copiar';
        btn.style.background = '';
      }, 2000);
    } catch {
      toast('No se pudo copiar el código', 'info');
    }
  });
});

// ── Auto-dismiss flash messages ───────────────────────────────────
const flashMsgs = document.querySelectorAll('.flash-msg');
flashMsgs.forEach(msg => {
  setTimeout(() => {
    msg.style.opacity = '0';
    msg.style.transform = 'translateX(80px)';
    msg.style.transition = 'all .4s ease';
    setTimeout(() => msg.remove(), 400);
  }, 4000);
});

// ── Init ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateCartBadge();
  loadStats();
});