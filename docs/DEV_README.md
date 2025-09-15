# Developer Documentation

## Branch Policy

### Branch Structure

- **dev-main**: Primary development branch for ongoing work
- **I1site**: Production branch for live site deployment
- **feature/*****: Feature-specific development branches
  - `feature/academy`: Academy functionality
  - `feature/ai-stylist`: AI styling features
  - `feature/auth`: Authentication system
  - `feature/rent`: Rental functionality
  - `feature/shop`: Shopping features
- **hotfix**: Emergency fixes for production issues

### Branch Workflow

1. **Feature Development**
   - Create feature branches from `dev-main`
   - Naming convention: `feature/descriptive-name`
   - Complete development and testing in feature branch
   - Submit pull request to merge into `dev-main`

2. **Development to Production**
   - All features merge into `dev-main` first
   - Thorough testing performed on `dev-main`
   - Stable releases merged from `dev-main` to `I1site`
   - `I1site` automatically deploys to production

3. **Emergency Fixes**
   - Create `hotfix` branch from `I1site`
   - Apply critical fixes
   - Merge to both `I1site` and `dev-main`

## Deployment Instructions

### GitHub Pages Deployment

The site automatically deploys from the `I1site` branch via GitHub Pages.

**Deployment Triggers:**
- Any push to `I1site` branch
- Successful merge of pull request to `I1site`

**Deployment Status:**
- Monitor deployments at: `/deployments`
- Current deployments: 22 total
- Latest deployment: github-pages

### Manual Deployment Steps

1. **Pre-deployment Checklist:**
   - [ ] All tests passing
   - [ ] Code reviewed and approved
   - [ ] Documentation updated
   - [ ] No console errors in browser
   - [ ] Mobile responsive testing complete

2. **Deployment Process:**
   ```bash
   # Switch to dev-main
   git checkout dev-main
   
   # Pull latest changes
   git pull origin dev-main
   
   # Switch to production branch
   git checkout I1site
   
   # Merge from dev-main
   git merge dev-main
   
   # Push to trigger deployment
   git push origin I1site
   ```

3. **Post-deployment Verification:**
   - [ ] Site loads successfully
   - [ ] Core functionality working
   - [ ] No broken links or images
   - [ ] Performance metrics acceptable

## Phase Checklists

### Phase 1: Foundation Setup ✅

**Completed Tasks:**
- [x] Repository structure established
- [x] Branch strategy implemented
- [x] Basic site framework created
- [x] GitHub Pages deployment configured
- [x] Domain setup (CNAME)
- [x] Initial documentation

**Files Created:**
- `index.html` - Main site entry point
- `admin.html` - Admin interface
- `css/` - Styling directory
- `js/` - JavaScript functionality
- `assets/images/logo/` - Logo assets
- `site-database.xlsx` - Data structure
- `CNAME` - Domain configuration

### Phase 2: Core Features (In Progress)

**Authentication System:**
- [ ] User registration
- [ ] Login/logout functionality
- [ ] Password reset
- [ ] User profiles
- [ ] Role-based access control

**Shop Functionality:**
- [ ] Product catalog
- [ ] Shopping cart
- [ ] Checkout process
- [ ] Payment integration
- [ ] Order management

**Rental System:**
- [ ] Rental product listings
- [ ] Booking calendar
- [ ] Availability management
- [ ] Rental pricing
- [ ] Return process

### Phase 3: Advanced Features (Planned)

**AI Stylist:**
- [ ] Style recommendation engine
- [ ] User preference learning
- [ ] Outfit coordination
- [ ] Trend analysis
- [ ] Personal styling advice

**Academy Module:**
- [ ] Course catalog
- [ ] Video content delivery
- [ ] Progress tracking
- [ ] Certification system
- [ ] Interactive learning tools

**Mobile Optimization:**
- [ ] Responsive design improvements
- [ ] Mobile-specific features
- [ ] App-like experience
- [ ] Offline capabilities
- [ ] Push notifications

### Phase 4: Performance & Analytics (Future)

**Performance Optimization:**
- [ ] Code splitting
- [ ] Lazy loading
- [ ] CDN integration
- [ ] Image optimization
- [ ] Caching strategies

**Analytics & Monitoring:**
- [ ] User behavior tracking
- [ ] Performance monitoring
- [ ] Error logging
- [ ] A/B testing framework
- [ ] Business metrics dashboard

## Development Guidelines

### Code Standards

- **HTML**: Semantic markup, accessibility compliance
- **CSS**: BEM methodology, mobile-first responsive design
- **JavaScript**: ES6+, modular architecture
- **Files**: Descriptive naming, proper organization

### Testing Requirements

- Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Mobile responsiveness (iOS, Android)
- Accessibility standards (WCAG 2.1)
- Performance benchmarks (< 3s load time)

### Documentation Standards

- Update this README for major changes
- Comment complex code sections
- Maintain changelog for releases
- Document API changes

## Quick Reference

### Important Links

- **Live Site**: [https://sujatafashion.github.io](https://sujatafashion.github.io)
- **Repository**: [ccoolavi/sujatafashion.github.io](https://github.com/ccoolavi/sujatafashion.github.io)
- **Issues**: [/issues](https://github.com/ccoolavi/sujatafashion.github.io/issues)
- **Pull Requests**: [/pulls](https://github.com/ccoolavi/sujatafashion.github.io/pulls)

### Key Files

- `index.html` - Main site entry
- `admin.html` - Admin interface
- `site-database.xlsx` - Data structure
- `test-workflow.md` - Testing procedures
- `docs/DEV_README.md` - This file

### Branch Status

- **dev-main**: Active development ✅
- **I1site**: Production ready ✅
- **feature branches**: Feature-specific development
- **hotfix**: Emergency fixes only

---

*Last updated: September 15, 2025*
*Branch: dev-main*
*Phase: 1 Complete, Phase 2 In Progress*
