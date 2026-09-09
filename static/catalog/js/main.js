/**
 * Synapse — Premium Event & Conference Template JavaScript
 * Core interactive elements and user experience micro-animations.
 */

document.addEventListener('DOMContentLoaded', function() {
  'use strict';

  // ==========================================================================
  // 1. Sticky Header Scroll Effect
  // ==========================================================================
  const navbar = document.querySelector('header .navbar');
  if (navbar) {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    };
    
    // Trigger on load in case page is refreshed while scrolled
    handleScroll();
    window.addEventListener('scroll', handleScroll);
  }

  // ==========================================================================
  // 2. Dynamic Countdown Timer (Event Launch)
  // ==========================================================================
  const daysEl = document.getElementById('days');
  const hoursEl = document.getElementById('hours');
  const minsEl = document.getElementById('minutes');
  const secsEl = document.getElementById('seconds');

  if (daysEl && hoursEl && minsEl && secsEl) {
    // Set event date to exactly 68 days in the future from current timestamp
    // so the landing page countdown timer is always ticking and active for reviewers.
    const targetDate = new Date(Date.now() + (68 * 24 * 60 * 60 * 1000) + (14 * 60 * 60 * 1000));

    function updateCountdown() {
      const now = new Date().getTime();
      const difference = targetDate - now;

      if (difference <= 0) {
        clearInterval(countdownInterval);
        daysEl.textContent = '000';
        hoursEl.textContent = '00';
        minsEl.textContent = '00';
        secsEl.textContent = '00';
        return;
      }

      const days = Math.floor(difference / (1000 * 60 * 60 * 24));
      const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((difference % (1000 * 60)) / 1000);

      // Display with padding
      daysEl.textContent = String(days).padStart(3, '0');
      hoursEl.textContent = String(hours).padStart(2, '0');
      minsEl.textContent = String(minutes).padStart(2, '0');
      secsEl.textContent = String(seconds).padStart(2, '0');
    }

    updateCountdown();
    const countdownInterval = setInterval(updateCountdown, 1000);
  }

  // ==========================================================================
  // 3. Stats Counter Increment Animation (IntersectionObserver)
  // ==========================================================================
  const statNumbers = document.querySelectorAll('.stat-number');
  
  if (statNumbers.length > 0) {
    const animateCounter = (el) => {
      const target = parseInt(el.getAttribute('data-target'), 10);
      const duration = 2000; // Animation duration in ms
      const stepTime = Math.max(Math.floor(duration / target), 15);
      let current = 0;
      
      // Calculate a step value for fast numbers (e.g. 5000)
      const increment = Math.ceil(target / (duration / stepTime));

      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          el.textContent = target;
          clearInterval(timer);
        } else {
          el.textContent = current;
        }
      }, stepTime);
    };

    const statsObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          animateCounter(el);
          observer.unobserve(el); // Only animate once
        }
      });
    }, {
      threshold: 0.5
    });

    statNumbers.forEach(stat => statsObserver.observe(stat));
  }

  // ==========================================================================
  // 4. Session Agenda Bookmarking (localStorage State)
  // ==========================================================================
  const bookmarkButtons = document.querySelectorAll('.btn-icon-bookmark');
  
  // Load bookmarked sessions
  let bookmarkedSessions = JSON.parse(localStorage.getItem('synapse_bookmarks')) || [];
  
  // Setup button visual state on initial load
  bookmarkButtons.forEach(btn => {
    const sessionId = btn.getAttribute('data-session-id');
    const icon = btn.querySelector('i');
    
    if (bookmarkedSessions.includes(sessionId)) {
      btn.classList.add('active');
      if (icon) {
        icon.classList.remove('bi-bookmark');
        icon.classList.add('bi-bookmark-fill');
      }
    }
  });

  // Toggle bookmark event handler
  bookmarkButtons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const sessionId = this.getAttribute('data-session-id');
      const icon = this.querySelector('i');
      
      this.classList.toggle('active');
      
      if (this.classList.contains('active')) {
        if (icon) {
          icon.classList.remove('bi-bookmark');
          icon.classList.add('bi-bookmark-fill');
        }
        if (!bookmarkedSessions.includes(sessionId)) {
          bookmarkedSessions.push(sessionId);
        }
        showToast('Session Bookmarked!', 'This talk has been added to your custom schedule agenda.');
      } else {
        if (icon) {
          icon.classList.remove('bi-bookmark-fill');
          icon.classList.add('bi-bookmark');
        }
        bookmarkedSessions = bookmarkedSessions.filter(id => id !== sessionId);
        showToast('Bookmark Removed', 'Talk removed from your custom schedule agenda.');
      }
      
      localStorage.setItem('synapse_bookmarks', JSON.stringify(bookmarkedSessions));
    });
  });

  // Simple Notification Toast System
  const showToast = (title, message) => {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.style.position = 'fixed';
      container.style.bottom = '24px';
      container.style.right = '24px';
      container.style.zIndex = '9999';
      container.style.display = 'flex';
      container.style.flexDirection = 'column';
      container.style.gap = '10px';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'glass-card p-3 shadow-lg';
    toast.style.minWidth = '280px';
    toast.style.maxWidth = '350px';
    toast.style.borderLeft = '4px solid var(--synapse-primary)';
    toast.style.background = 'rgba(18, 24, 41, 0.95)';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
    toast.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';

    toast.innerHTML = `
      <div class="d-flex justify-content-between align-items-start mb-1">
        <h6 class="mb-0 text-white font-heading fw-bold">${title}</h6>
        <button type="button" class="btn-close btn-close-white" style="font-size: 0.7rem; padding: 0;" aria-label="Close"></button>
      </div>
      <p class="mb-0 text-muted small">${message}</p>
    `;

    container.appendChild(toast);

    // Fade in
    setTimeout(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';
    }, 50);

    // Dismiss button click handler
    const closeBtn = toast.querySelector('.btn-close');
    closeBtn.addEventListener('click', () => dismissToast(toast));

    // Auto fade out after 3.5 seconds
    setTimeout(() => dismissToast(toast), 3500);
  };

  const dismissToast = (toast) => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-20px)';
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  };

  // ==========================================================================
  // 5. Pricing Dynamic Calculator Toggle (Corporate Discount)
  // ==========================================================================
  const pricingToggle = document.getElementById('pricingToggle');
  const priceStandardEl = document.getElementById('priceStandard');
  const priceVipEl = document.getElementById('priceVip');
  const priceEnterpriseEl = document.getElementById('priceEnterprise');
  
  const labelInd = document.getElementById('billingLabelInd');
  const labelCorp = document.getElementById('billingLabelCorp');

  if (pricingToggle && priceStandardEl && priceVipEl && priceEnterpriseEl) {
    const originalPrices = {
      standard: 199,
      vip: 399,
      enterprise: 799
    };
    
    pricingToggle.addEventListener('change', function() {
      if (this.checked) {
        // Apply 20% discount
        animatePriceUpdate(priceStandardEl, Math.round(originalPrices.standard * 0.8));
        animatePriceUpdate(priceVipEl, Math.round(originalPrices.vip * 0.8));
        animatePriceUpdate(priceEnterpriseEl, Math.round(originalPrices.enterprise * 0.8));
        
        // Update label typography emphasis
        if (labelInd) labelInd.className = 'fw-bold font-heading text-secondary';
        if (labelCorp) labelCorp.className = 'fw-bold font-heading text-white d-flex align-items-center gap-2';
      } else {
        // Revert to original
        animatePriceUpdate(priceStandardEl, originalPrices.standard);
        animatePriceUpdate(priceVipEl, originalPrices.vip);
        animatePriceUpdate(priceEnterpriseEl, originalPrices.enterprise);
        
        if (labelInd) labelInd.className = 'fw-bold font-heading text-white';
        if (labelCorp) labelCorp.className = 'fw-bold font-heading text-secondary d-flex align-items-center gap-2';
      }
    });
  }

  // Smooth slide counter transition for prices
  function animatePriceUpdate(element, targetPrice) {
    const currentPrice = parseInt(element.textContent, 10);
    const difference = targetPrice - currentPrice;
    const duration = 300; // Animation duration in ms
    const stepTime = 15;
    const steps = duration / stepTime;
    const increment = difference / steps;
    let stepCount = 0;
    
    const priceTimer = setInterval(() => {
      stepCount++;
      const nextVal = currentPrice + (increment * stepCount);
      element.textContent = Math.round(nextVal);
      
      if (stepCount >= steps) {
        element.textContent = targetPrice;
        clearInterval(priceTimer);
      }
    }, stepTime);
  }

  // ==========================================================================
  // 6. Newsletter Subscription Form AJAX-simulation
  // ==========================================================================
  const newsletterForm = document.getElementById('newsletterForm');
  const newsletterSuccess = document.getElementById('newsletterSuccess');

  if (newsletterForm && newsletterSuccess) {
    newsletterForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const submitBtn = this.querySelector('button[type="submit"]');
      const originalText = submitBtn.textContent;
      
      // Spinner feedback
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Subscribing...`;

      // Mock delay
      setTimeout(() => {
        newsletterForm.reset();
        newsletterForm.style.display = 'none';
        newsletterSuccess.classList.remove('d-none');
        showToast('Subscribed Successfully!', 'Thank you for subscribing to Synapse updates.');
      }, 1500);
    });
  }

  // Mobile menu click outside close
  const navbarCollapse = document.getElementById("navbarContent");
  const navbarToggler = document.querySelector(".navbar-toggler");
  
  if (navbarCollapse && navbarToggler) {
    document.addEventListener("click", (e) => {
      const isClickedInside = navbarCollapse.contains(e.target) || navbarToggler.contains(e.target);
      if (!isClickedInside && navbarCollapse.classList.contains("show")) {
        navbarToggler.click(); // Close drawer
      }
    });
  }
});
