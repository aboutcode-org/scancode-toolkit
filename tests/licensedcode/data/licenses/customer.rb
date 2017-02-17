module Braintree
  # See http://www.braintreepayments.com/docs/ruby
  class Customer
    include BaseModule

    attr_reader :addresses, :company, :created_at, :credit_cards, :email, :fax, :first_name, :id, :last_name,
      :phone, :updated_at, :website, :custom_fields

    # See http://www.braintreepayments.com/docs/ruby/customers/search
    def self.all
      Configuration.gateway.customer.all
    end

    # See http://www.braintreepayments.com/docs/ruby/customers/create
    def self.create(attributes = {})
      Configuration.gateway.customer.create(attributes)
    end

    # See http://www.braintreepayments.com/docs/ruby/customers/create
    def self.create!(attributes = {})
      return_object_or_raise(:customer) { create(attributes) }
    end

    # Deprecated. Use Braintree::TransparentRedirect.url
    #
    # See http://www.braintreepayments.com/docs/ruby/customers/create_tr
    def self.create_customer_url
      warn "[DEPRECATED] Customer.create_customer_url is deprecated. Please use TransparentRedirect.url"
      Configuration.gateway.customer.create_customer_url
    end

    # Deprecated. Use Braintree::TransparentRedirect.confirm
    #
    # See http://www.braintreepayments.com/docs/ruby/customers/create_tr
    def self.create_from_transparent_redirect(query_string)
      warn "[DEPRECATED] Customer.create_from_transparent_redirect is deprecated. Please use TransparentRedirect.confirm"
      Configuration.gateway.customer.create_from_transparent_redirect(query_string)
    end

    # See http://www.braintreepayments.com/docs/ruby/transactions/create_from_vault
    def self.credit(customer_id, transaction_attributes)
      Transaction.credit(transaction_attributes.merge(:customer_id => customer_id))
    end

    # See http://www.braintreepayments.com/docs/ruby/transactions/create_from_vault
    def self.credit!(customer_id, transaction_attributes)
       return_object_or_raise(:transaction){ credit(customer_id, transaction_attributes) }
    end

    # See http://www.braintreepayments.com/docs/ruby/customers/delete
    def self.delete(customer_id)
      Configuration.gateway.customer.delete(customer_id)
    end

    # See http://www.braintreepayments.com/docs/ruby/customers/search
    def self.find(customer_id)
      Configuration.gateway.customer.find(customer_id)
    end

    # See http://www.braintreepayments.com/docs/ruby/transactions/create_from_vault
    def self.sale(customer_id, transaction_attributes)
      Transaction.sale(transaction_attributes.merge(:customer_id => customer_id))
    end

    # See http://www.braintreepayments.com/docs/ruby/transactions/create_from_vault
    def self.sale!(customer_id, transaction_attributes)
      return_object_or_raise(:transaction) { sale(customer_id, transaction_attributes) }
    end

    # See http://www.braintreepayments.com/docs/ruby/customers/search
    def self.search(&block)
      Configuration.gateway.customer.search(&block)
    end

    # Returns a ResourceCollection of transactions for the customer with the given +customer_id+.
    def self.transactions(customer_id, options = {})
      Configuration.gateway.customer.transactions(customer_id, options = {})
    end

    # See http://www.braintreepayments.com/docs/ruby/customers/update
    def self.update(customer_id, attributes)
      Configuration.gateway.customer.update(customer_id, attributes)
    end

    # See http://www.braintreepayments.com/docs/ruby/customers/update
    def self.update!(customer_id, attributes)
      return_object_or_raise(:customer) { update(customer_id, attributes) }
    end

    # Deprecated. Use Braintree::TransparentRedirect.url
    #
    # See http://www.braintreepayments.com/docs/ruby/customers/update_tr
    def self.update_customer_url
      warn "[DEPRECATED] Customer.update_customer_url is deprecated. Please use TransparentRedirect.url"
      Configuration.gateway.customer.update_customer_url
    end

    # Deprecated. Use Braintree::TransparentRedirect.confirm
    #
    # See http://www.braintreepayments.com/docs/ruby/customers/update_tr
    def self.update_from_transparent_redirect(query_string)
      warn "[DEPRECATED] Customer.update_from_transparent_redirect is deprecated. Please use TransparentRedirect.confirm"
      Configuration.gateway.customer.update_from_transparent_redirect(query_string)
    end

    def initialize(gateway, attributes) # :nodoc:
      @gateway = gateway
      set_instance_variables_from_hash(attributes)
      @credit_cards = (@credit_cards || []).map { |pm| CreditCard._new gateway, pm }
      @addresses = (@addresses || []).map { |addr| Address._new gateway, addr }
    end

    # See http://www.braintreepayments.com/docs/ruby/transactions/create_from_vault
    def credit(transaction_attributes)
      @gateway.transaction.credit(transaction_attributes.merge(:customer_id => id))
    end

    # See http://www.braintreepayments.com/docs/ruby/transactions/create_from_vault
    def credit!(transaction_attributes)
      return_object_or_raise(:transaction) { credit(transaction_attributes) }
    end

    # See http://www.braintreepayments.com/docs/ruby/customers/delete
    def delete
      @gateway.customer.delete(id)
    end

    def inspect # :nodoc:
      first = [:id]
      last = [:addresses, :credit_cards]
      order = first + (self.class._attributes - first - last) + last
      nice_attributes = order.map do |attr|
        "#{attr}: #{send(attr).inspect}"
      end
      "#<#{self.class} #{nice_attributes.join(', ')}>"
    end

    # Deprecated. Use Braintree::Customer.sale
    #
    # See http://www.braintreepayments.com/docs/ruby/transactions/create_from_vault
    def sale(transaction_attributes)
      warn "[DEPRECATED] sale as an instance method is deprecated. Please use Customer.sale"
      @gateway.transaction.sale(transaction_attributes.merge(:customer_id => id))
    end

    # Deprecated. Use Braintree::Customer.sale!
    #
    # See http://www.braintreepayments.com/docs/ruby/transactions/create_from_vault
    def sale!(transaction_attributes)
      warn "[DEPRECATED] sale! as an instance method is deprecated. Please use Customer.sale!"
      return_object_or_raise(:transaction) { sale(transaction_attributes) }
    end

    # Returns a ResourceCollection of transactions for the customer.
    def transactions(options = {})
      @gateway.customer.transactions(id, options)
    end

    # Deprecated. Use Braintree::Customer.update
    #
    # See http://www.braintreepayments.com/docs/ruby/customers/update
    def update(attributes)
      warn "[DEPRECATED] update as an instance method is deprecated. Please use Customer.update"
      result = @gateway.customer.update(id, attributes)
      if result.success?
        copy_instance_variables_from_object result.customer
      end
      result
    end

    # Deprecated. Use Braintree::Customer.update!
    #
    # See http://www.braintreepayments.com/docs/ruby/customers/update
    def update!(attributes)
      warn "[DEPRECATED] update! as an instance method is deprecated. Please use Customer.update!"
      return_object_or_raise(:customer) { update(attributes) }
    end

    # Returns true if +other+ is a Customer with the same id
    def ==(other)
      return false unless other.is_a?(Customer)
      id == other.id
    end

    class << self
      protected :new
    end

    def self._new(*args) # :nodoc:
      self.new *args
    end

    def self._attributes # :nodoc:
      [
        :addresses, :company, :credit_cards, :email, :fax, :first_name, :id, :last_name, :phone, :website,
        :created_at, :updated_at
      ]
    end
  end
end
